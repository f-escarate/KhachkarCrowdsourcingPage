const { MODE } = import.meta.env;
export const HOST = MODE === 'development' ? 'http://localhost:8000' : 'https://saduewa.dcc.uchile.cl/crowdsourcing_backend';
export const MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/museum/';
export const ONLINE_MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/online-museum/';
export const TEXT_FIELDS_WO_DATE = {
    'location': 'Location',
    'latLong': 'Latitude',
    'scenario': 'Scenario',
    'setting': 'Setting',
    'landscape': 'Landscape',
    'accessibility': 'Accessibility',
    'masters_name': 'Master',
    'category': 'Category',
    'production_period': 'Production Period',
    'motive': 'Motive',
    'condition_of_preservation': 'Condition of Preservation',
    'inscription': 'Inscription',
    'important_features': 'Important',
    'backside': 'Backside',
    'history_ownership': 'History',
    'commemorative_activities': 'Commemorative Activities',
    'references': 'References',
}
export const TEXT_FIELDS = {...TEXT_FIELDS_WO_DATE, 'date': 'Upload Date'}
