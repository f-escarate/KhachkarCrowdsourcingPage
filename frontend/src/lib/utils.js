import { HOST } from "$lib/constants";
import Cookies from 'js-cookie';

export function addAnimationStyles(targets, styles) {
    const options = {
        root: null, // use the viewport as the root
        rootMargin: '0px',
        threshold: 0.5, // change this value as needed, 0.5 means when 50% of the element is visible
    };
    for (let i = 0; i < targets.length; i++){
        let target = targets[i];
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    for (let style of styles)
                        entry.target.classList.add(style);
                    observer.unobserve(entry.target);
                }
            });
        }, options);

        if (target) 
            observer.observe(target);
    }
}

export const auth_get_json = async (url) => {
    let response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${Cookies.get('access_token')}`
        }
    });
    if (response.status === 401) {
        response = await fetch(`${HOST}/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Cookies.get('refresh_token')}`
            }
        });
        if (response.status === 200) {
            const data = await response.json();
            let access_token = data.access_token;
            Cookies.set('access_token', access_token, { sameSite:'strict', secure:true });
            response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${access_token}`
                }
            });
        }
        else {
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            alert('Session expired. Please login again.');
            window.location.href = '/login';
        }
    }
    return response;
}

export const get_json = (url) => {
    return fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    });
}

export const auth_post_request = async (url, data, method='POST', json=false) => {
    let get_headers = json? (token) => ({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    }) : (token) => ({
        'Authorization': `Bearer ${token}`
    });

    let response = await fetch(url, {
        method: method,
        headers: get_headers(),
        body: data
    });

    if (response.status === 401) {
        response = await fetch(`${HOST}/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Cookies.get('refresh_token')}`
            }
        });
        if (response.status === 200) {
            const access_token_response = await response.json();
            let access_token = access_token_response.access_token;
            Cookies.set('access_token', access_token, { sameSite:'strict', secure:true });
            response = await fetch(url, {
                method: method,
                headers: get_headers(access_token),
                body: data
            });
        }
        else {
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            alert('Session expired. Please login again.');
            window.location.href = '/login';
        }
    }
    return response;
}