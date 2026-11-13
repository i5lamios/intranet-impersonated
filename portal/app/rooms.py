"""Meeting rooms: free/busy of Exchange room mailboxes (EWS GetUserAvailability, NTLM as svc-intranet) and booking.

ROOMS = "Name|room@example.com;Name 2|room2@example.com". A booking is a meeting created in the BOOKER's own calendar
(EWS ExchangeImpersonation; svc-intranet holds ApplicationImpersonation scoped to "Intranet booking users" = user
mailboxes, granted 2026-11-01): the booker is the organizer, invitations / updates / cancellations go out from them,
the room auto-accepts if free. Older bookings (organizer NULL) live in the intranet@ calendar.
Outlook bookings (room added to a meeting) keep working as before. Subjects are shown only if the room calendar shares details
(Set-MailboxFolderPermission room:\\Calendar -User Default -AccessRights LimitedDetails).
"""
import os
import threading
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from xml.sax.saxutils import escape

import requests
from requests_ntlm import HttpNtlmAuth

from .core import secret

EWS = os.environ.get("EWS_URL", "https://mail.example.com/EWS/Exchange.asmx")
USER = os.environ.get("EWS_USER", "COMPANY\\svc-intranet")
ROOMS = [tuple(x.split("|", 1)) for x in os.environ.get("ROOMS", "").split(";") if "|" in x]
TTL = 5          # seconds; the rooms page polls every 3 s, so Exchange sees at most one request per day-view per 5 s
NS = {"m": "http://schemas.microsoft.com/exchange/services/2006/messages",
      "t": "http://schemas.microsoft.com/exchange/services/2006/types"}


def _password():
    return secret("SVC_PASSWORD", "")


def _request(day: date, mails=None, view="Detailed"):
    """Room mailboxes by default; with mails: those people, free/busy only (no subjects)."""
    kind, boxes = ("Required", mails) if mails else ("Room", [m for _, m in ROOMS])
    mailboxes = "".join(f"<t:MailboxData><t:Email><t:Address>{escape(m)}</t:Address></t:Email>"
                        f"<t:AttendeeType>{kind}</t:AttendeeType></t:MailboxData>" for m in boxes)
    start, end = datetime.combine(day, datetime.min.time()), datetime.combine(day + timedelta(days=1), datetime.min.time())
    # Asia/Baku = UTC+4 all year (bias is minutes to add to local time to get UTC). No DST, but Exchange rejects
    # identical standard/daylight transitions ("time zone isn't valid") → two different months, both with bias 0.
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="{NS['t']}" xmlns:m="{NS['m']}">
<soap:Header><t:RequestServerVersion Version="Exchange2013"/></soap:Header><soap:Body>
<m:GetUserAvailabilityRequest>
<t:TimeZone><t:Bias>-240</t:Bias><t:StandardTime><t:Bias>0</t:Bias><t:Time>00:00:00</t:Time><t:DayOrder>1</t:DayOrder><t:Month>10</t:Month><t:DayOfWeek>Sunday</t:DayOfWeek></t:StandardTime>
<t:DaylightTime><t:Bias>0</t:Bias><t:Time>00:00:00</t:Time><t:DayOrder>1</t:DayOrder><t:Month>3</t:Month><t:DayOfWeek>Sunday</t:DayOfWeek></t:DaylightTime></t:TimeZone>
<m:MailboxDataArray>{mailboxes}</m:MailboxDataArray>
<t:FreeBusyViewOptions><t:TimeWindow><t:StartTime>{start:%Y-%m-%dT%H:%M:%S}</t:StartTime><t:EndTime>{end:%Y-%m-%dT%H:%M:%S}</t:EndTime></t:TimeWindow>
<t:MergedFreeBusyIntervalInMinutes>30</t:MergedFreeBusyIntervalInMinutes><t:RequestedView>{view}</t:RequestedView></t:FreeBusyViewOptions>
</m:GetUserAvailabilityRequest></soap:Body></soap:Envelope>"""


class Rooms:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    @property
    def enabled(self):
        return bool(ROOMS and _password())

    def names(self):
        return [{"name": n, "mail": m} for n, m in ROOMS]

    def forget(self, day: date):
        with self._lock:
            self._cache.pop(day.isoformat(), None)

    def day(self, day: date):
        key = day.isoformat()
        with self._lock:
            hit = self._cache.get(key)
            if hit and time.time() - hit[0] < TTL:
                return hit[1]
        r = requests.post(EWS, data=_request(day).encode(), timeout=20, auth=HttpNtlmAuth(USER, _password()),
                          headers={"Content-Type": "text/xml; charset=utf-8"})
        r.raise_for_status()
        doc = ET.fromstring(r.content)
        out = []
        for (name, mail), resp in zip(ROOMS, doc.iter(f"{{{NS['m']}}}FreeBusyResponse")):
            code = resp.find("m:ResponseMessage", NS)
            events = []
            for ev in resp.iter(f"{{{NS['t']}}}CalendarEvent"):
                status = ev.findtext("t:BusyType", "", NS)
                if status in ("Free", "NoData"):
                    continue
                det = ev.find("t:CalendarEventDetails", NS)
                events.append({"start": ev.findtext("t:StartTime", "", NS)[:16], "end": ev.findtext("t:EndTime", "", NS)[:16],
                               "status": status, "subject": det.findtext("t:Subject", "", NS) if det is not None else ""})
            out.append({"name": name, "mail": mail, "events": sorted(events, key=lambda e: e["start"]),
                        "error": None if code is None or code.get("ResponseClass") == "Success" else code.get("ResponseClass")})
        with self._lock:
            self._cache[key] = (time.time(), out)
        return out


def availability(mails, start: datetime, end: datetime):
    """Is each colleague free in this slot? {mail: Free | Tentative | Busy | OOF | Unknown}. Busy/free only, never subjects."""
    r = requests.post(EWS, data=_request(start.date(), mails, "FreeBusy").encode(), timeout=20, auth=HttpNtlmAuth(USER, _password()),
                      headers={"Content-Type": "text/xml; charset=utf-8"})
    r.raise_for_status()
    s1, e1 = start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")
    rank, out = ["Free", "Tentative", "Busy", "OOF"], {}
    for mail, resp in zip(mails, ET.fromstring(r.content).iter(f"{{{NS['m']}}}FreeBusyResponse")):
        code = resp.find("m:ResponseMessage", NS)
        if code is not None and code.get("ResponseClass") != "Success":
            out[mail] = "Unknown"
            continue
        best = "Free"
        for ev in resp.iter(f"{{{NS['t']}}}CalendarEvent"):
            st = ev.findtext("t:BusyType", "", NS)
            if st in rank and ev.findtext("t:StartTime", "", NS)[:16] < e1 and ev.findtext("t:EndTime", "", NS)[:16] > s1 and rank.index(st) > rank.index(best):
                best = st
        out[mail] = best
    return out


def _ews(body, as_user=None):
    imp = (f"<t:ExchangeImpersonation><t:ConnectingSID><t:PrimarySmtpAddress>{escape(as_user)}</t:PrimarySmtpAddress>"
           f"</t:ConnectingSID></t:ExchangeImpersonation>") if as_user else ""
    env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="{NS['t']}" xmlns:m="{NS['m']}">
<soap:Header><t:RequestServerVersion Version="Exchange2013"/>{imp}</soap:Header><soap:Body>{body}</soap:Body></soap:Envelope>"""
    r = requests.post(EWS, data=env.encode(), timeout=30, auth=HttpNtlmAuth(USER, _password()),
                      headers={"Content-Type": "text/xml; charset=utf-8"})
    if r.status_code == 500 and b"ErrorImpersonate" in r.content:
        raise RuntimeError("no impersonation right for this mailbox")
    r.raise_for_status()
    doc = ET.fromstring(r.content)
    msg = next(doc.iter(f"{{{NS['m']}}}ResponseCode"), None)
    if msg is not None and msg.text != "NoError":
        raise RuntimeError(msg.text)
    return doc


def _people(tag, mails):
    return (f"<t:{tag}>" + "".join(f"<t:Attendee><t:Mailbox><t:EmailAddress>{escape(m)}</t:EmailAddress></t:Mailbox></t:Attendee>"
                                   for m in mails) + f"</t:{tag}>") if mails else ""


def _room_name(room_mail):
    return dict((m, n) for n, m in ROOMS).get(room_mail, room_mail)


def book(room_mail, start: datetime, end: datetime, subject, organizer, attendees=(), note=""):
    """Meeting in the organizer's calendar (impersonated). start/end: naive Asia/Baku times. Returns the EWS item id."""
    body = f"<p>Room booked on the Company Intranet — change or cancel it there or here in Outlook.</p>{note}"
    doc = _ews(f"""<m:CreateItem SendMeetingInvitations="SendToAllAndSaveCopy">
<m:SavedItemFolderId><t:DistinguishedFolderId Id="calendar"/></m:SavedItemFolderId><m:Items><t:CalendarItem>
<t:Subject>{escape(subject)}</t:Subject><t:Body BodyType="HTML">{escape(body)}</t:Body>
<t:Start>{start:%Y-%m-%dT%H:%M:%S}+04:00</t:Start><t:End>{end:%Y-%m-%dT%H:%M:%S}+04:00</t:End>
<t:Location>{escape(_room_name(room_mail))}</t:Location>
{_people("RequiredAttendees", attendees)}{_people("Resources", [room_mail])}
</t:CalendarItem></m:Items></m:CreateItem>""", as_user=organizer)
    return next(doc.iter(f"{{{NS['t']}}}ItemId")).get("Id")


def update(item_id, organizer, room_mail, start: datetime, end: datetime, subject, attendees):
    """Change time / room / subject / attendees; Exchange sends the update (and cancellations to removed people)."""
    f = lambda uri, inner: (f'<t:SetItemField><t:FieldURI FieldURI="{uri}"/><t:CalendarItem>{inner}</t:CalendarItem></t:SetItemField>')
    changes = (f("item:Subject", f"<t:Subject>{escape(subject)}</t:Subject>")
               + f("calendar:Start", f"<t:Start>{start:%Y-%m-%dT%H:%M:%S}+04:00</t:Start>")
               + f("calendar:End", f"<t:End>{end:%Y-%m-%dT%H:%M:%S}+04:00</t:End>")
               + f("calendar:Location", f"<t:Location>{escape(_room_name(room_mail))}</t:Location>")
               + (f("calendar:RequiredAttendees", _people("RequiredAttendees", attendees)) if attendees
                  else '<t:DeleteItemField><t:FieldURI FieldURI="calendar:RequiredAttendees"/></t:DeleteItemField>')
               + f("calendar:Resources", _people("Resources", [room_mail])))
    _ews(f"""<m:UpdateItem ConflictResolution="AlwaysOverwrite" SendMeetingInvitationsOrCancellations="SendToAllAndSaveCopy">
<m:ItemChanges><t:ItemChange><t:ItemId Id="{escape(item_id)}"/><t:Updates>{changes}</t:Updates></t:ItemChange></m:ItemChanges>
</m:UpdateItem>""", as_user=organizer)


def attendees_of(item_id, organizer):
    """Current required attendees of the meeting (as Exchange has them — the organizer may have changed them in Outlook)."""
    doc = _ews(f"""<m:GetItem><m:ItemShape><t:BaseShape>IdOnly</t:BaseShape><t:AdditionalProperties>
<t:FieldURI FieldURI="calendar:RequiredAttendees"/></t:AdditionalProperties></m:ItemShape>
<m:ItemIds><t:ItemId Id="{escape(item_id)}"/></m:ItemIds></m:GetItem>""", as_user=organizer)
    req = next(doc.iter(f"{{{NS['t']}}}RequiredAttendees"), None)
    return [e.text.lower() for e in req.iter(f"{{{NS['t']}}}EmailAddress") if e.text] if req is not None else []


def cancel(item_id, organizer=None):
    try:
        _ews(f"""<m:DeleteItem DeleteType="MoveToDeletedItems" SendMeetingCancellations="SendToAllAndSaveCopy">
<m:ItemIds><t:ItemId Id="{escape(item_id)}"/></m:ItemIds></m:DeleteItem>""", as_user=organizer)
    except RuntimeError as e:
        if "ErrorItemNotFound" not in str(e):      # already deleted in Outlook → nothing left to cancel
            raise


def organizers(room_mail, day: date):
    """Who booked what in a room calendar (svc-intranet has Reviewer on the room calendars, granted 2026-11-02).
    → {("YYYY-MM-DDTHH:MM", "YYYY-MM-DDTHH:MM") Baku time: organizer display name}."""
    doc = _ews(f"""<m:FindItem Traversal="Shallow"><m:ItemShape><t:BaseShape>IdOnly</t:BaseShape><t:AdditionalProperties>
<t:FieldURI FieldURI="calendar:Start"/><t:FieldURI FieldURI="calendar:End"/><t:FieldURI FieldURI="calendar:Organizer"/>
</t:AdditionalProperties></m:ItemShape>
<m:CalendarView StartDate="{day:%Y-%m-%d}T00:00:00+04:00" EndDate="{day + timedelta(days=1):%Y-%m-%d}T00:00:00+04:00"/>
<m:ParentFolderIds><t:DistinguishedFolderId Id="calendar"><t:Mailbox><t:EmailAddress>{escape(room_mail)}</t:EmailAddress></t:Mailbox>
</t:DistinguishedFolderId></m:ParentFolderIds></m:FindItem>""")
    baku = lambda s: (datetime.fromisoformat(s.replace("Z", "+00:00")) + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M")
    out = {}
    for it in doc.iter(f"{{{NS['t']}}}CalendarItem"):
        s, e = it.find("t:Start", NS), it.find("t:End", NS)
        name = it.find("t:Organizer/t:Mailbox/t:Name", NS)
        if s is not None and e is not None and name is not None and name.text:
            out[(baku(s.text), baku(e.text))] = name.text
    return out
