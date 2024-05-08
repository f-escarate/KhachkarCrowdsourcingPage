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

export const auth_get_json = (url, token) => {
    return fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });
}

export const auth_post_request = (url, token, data) => {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: data
    });
}