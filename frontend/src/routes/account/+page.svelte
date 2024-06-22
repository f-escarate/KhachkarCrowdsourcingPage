<script>
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import { auth_get_json } from '$lib/utils';
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';
    import { Button } from 'flowbite-svelte';
    let data = {
        name: '',
        email: '',
        image: '',
    };
    let authenticated = false;
    onMount(async () => {
        if(Cookies.get('access_token') === undefined) {
            alert("You have to be logged in to access this page");
            window.location.href = `${base}/enter/login`;
            return;
        }
        const response = await auth_get_json(`${HOST}/me/`);
        const json = await response.json();
        if (json.status == 'success') {
            data.name = json.username;
            data.email = json.email;
            data.image = '';
            authenticated = true;
        } else {
            authenticated = false;
            Cookies.remove('access_token');
        }
    });
</script>

<div>
    <h1 class='text-4xl font-bold'>My Profile</h1>
    <div class='my-4 text-xl flex flex-col gap-1'>
        <h2><b class='text-2xl font-semibold'>Name:</b> {data.name}</h2>
        <h2><b class='text-2xl font-semibold'>Email:</b> {data.email}</h2>
    </div>
    <Button href={`${base}/account/changePassword`}>Change password</Button>
</div>