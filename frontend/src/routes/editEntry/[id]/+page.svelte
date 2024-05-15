<script>
    import Form from '../../../components/Form.svelte';
    import Cookies from 'js-cookie';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import { onMount } from 'svelte';

    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let token = null;
    let entry = {};
    let form;
    onMount(async () => {
        token = Cookies.get('token');
        if (token===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/login`;
            }
        }
        const response = await fetch(`${HOST}/get_khachkar/${id}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const json = await response.json();
        entry = json;
        let extension = entry.image;
        let vid_extension = entry.video;
        const img_response = await fetch(`${HOST}/get_image/${entry.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry.image}`
            }
        });
        const vid_response = await fetch(`${HOST}/get_video/${entry.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry.video}`
            }
        });
        entry.image = new File([await img_response.blob()], `image.${extension}`);
        entry.video = new File([await vid_response.blob()], `video.${vid_extension}`);
        form.previewFile('previewImage', entry.image);
        form.previewFile('previewVideo', entry.video);
        let videoElement = document.getElementById('videoElement');
        videoElement.load();
    });
    const handlePost = () => {
        alert("Khachkar has been edited successfully");
        window.location.href = `${base}/viewKhachkars/`;
    }
</script>

{#if token}
    <h1 id='edit_khach_title' class='text-4xl font-bold'>Edit Khachkar #{entry.id}</h1>
    <Form bind:this={form} on:post_data={handlePost} token={token} entry={entry} videoVisibility=1 endpoint_url={`/update_khachkar/${id}`} http_method='PATCH' button_text='Edit Khachkar'/>
{/if}