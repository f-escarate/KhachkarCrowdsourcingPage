const { MODE } = import.meta.env;
export const HOST = MODE === 'development' ? 'http://localhost:8000' : 'https://saduewa.dcc.uchile.cl/crowdsourcing_backend';
export const MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/museum/';
export const ONLINE_MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/online-museum/';
export const TEXT_FIELDS_WO_DATE = {
    'location': 'Location',
    'latLong': 'Latitude',
    'landscape': 'Landscape',
    'accessibility': 'Accessibility',
    'production_period': 'Production Period',
    'condition_of_preservation': 'Condition of Preservation',
    'inscription': 'Inscription',
    'important_features': 'Important',
    'references': 'References',
}
export const TEXT_FIELDS = {...TEXT_FIELDS_WO_DATE, 'date': 'Upload Date'}
const TEXT_FIELDS_LIST = Object.keys(TEXT_FIELDS);
export const BASE_ENTRY = TEXT_FIELDS_LIST.reduce((acc, key) => {
    acc[key] = '';
    return acc;
}
, {video: null, image: null});
export const BASE_MESH_DATA = {
    withMesh: false,
    mesh: null,
    material: null,
    images: []
}
