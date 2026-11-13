import Keycloak from 'keycloak-js';

export const kc = new Keycloak({url: 'https://sso.example.com', realm: 'company', clientId: 'intranet'});
