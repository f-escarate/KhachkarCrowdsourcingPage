import { error } from '@sveltejs/kit';
/** @type {import('./$types').PageLoad} */
export function load({ params }) {
    if (params.loginOrRegister !== undefined)
        return {
            loginOrRegister: params.loginOrRegister
        };
    error(404, 'Not found');
}