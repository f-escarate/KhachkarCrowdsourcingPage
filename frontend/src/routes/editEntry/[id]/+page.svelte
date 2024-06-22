<script>
    import Form from '../../../components/Form.svelte';
    import Cookies from 'js-cookie';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import { onMount } from 'svelte';

    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let entry = {};
    let form;
    onMount(async () => {
        if (Cookies.get('access_token')===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/enter/login`;
            }
        }
        const response = await fetch(`${HOST}/get_khachkar/with_enums/${id}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const json = await response.json();
        entry = json;
        let extension = entry.image;
        const img_response = await fetch(`${HOST}/get_image/${entry.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry.image}`
            }
        });
        entry.image = new File([await img_response.blob()], `image.${extension}`);
        form.previewFile('previewImage', entry.image);
    });
    const handlePost = () => {
        alert("Khachkar has been edited successfully");
        window.location.href = `${base}/viewKhachkars/`;
    }
</script>

<h1 id='edit_khach_title' class='text-4xl font-bold'>Edit Khachkar #{entry.id}</h1>
<Form 
    bind:this={form}
    on:post_data={handlePost}
    entry={entry}
    endpoint_url={`/update_khachkar/${id}`}
    http_method='PATCH'
    button_text='Edit Khachkar'
    use_video_or_mesh={false}
/>