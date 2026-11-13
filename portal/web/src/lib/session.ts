// Who is signed in (from /api/me) and the unsaved-changes guard shared by editors and the router.
export type Me = {
  username: string; name: string; email: string; editor: boolean;
  roles: {news: boolean; hse: boolean; it: boolean};
  features: {docs: boolean; rooms: boolean; rooms_list: string[]; phone: string; pbx: boolean; profile: boolean};
};
export const session: {me: Me | null} = {me: null};
export const guard = {dirty: false};
export const confirmLeave = (msg: string) => !guard.dirty || confirm(msg);
