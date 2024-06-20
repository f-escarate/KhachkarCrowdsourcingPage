const { MODE } = import.meta.env;
export const HOST = MODE === 'development' ? 'http://localhost:8000' : 'https://saduewa.dcc.uchile.cl/crowdsourcing_backend';
export const MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/museum/';
export const ONLINE_MUSEUM_URL = 'https://saduewa.dcc.uchile.cl/online-museum/';
export const TEXT_FIELDS_NAMES = {
    'production_period': 'Production Period',
    'inscription': 'Inscription text',
    'important_features': 'Important features (Description)',
    'references': 'References',
}

export const NUM_FIELDS_NAMES = {
    'latitude': 'Latitude',
    'longitude': 'Longitude',
    'height': 'Height (in meters)',
}

export const OPTION_FIELDS_NAMES = {
    'location': 'Location',
    'landscape': 'Landscape',
    'accessibility': 'Accessibility level',
    'condition_of_preservation': 'Condition of Preservation',
}

export const BASE_ENTRY = 
    Object.keys(TEXT_FIELDS_NAMES).reduce((acc, key) => {
        acc[key] = '';
        return acc;
    },   
    Object.keys(OPTION_FIELDS_NAMES).reduce((acc, key) => {
        acc[key] = 0;
        return acc;
    }, {
        'latitude': 40.0691,
        'longitude': 45.0382,
        'height': 3.0,
        date: '',
        video: null,
        image: null
    }));

export const BASE_MESH_DATA = {
    withMesh: false,
    mesh: null,
    material: null,
    images: []
}
