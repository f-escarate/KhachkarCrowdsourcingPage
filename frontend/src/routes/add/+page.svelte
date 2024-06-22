<script>
    import Form from '../../components/Form.svelte';
    import { base } from "$app/paths";
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';
    onMount(() => {
        if (Cookies.get('access_token')===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/enter/login`;
            }
        }
    });
    const handlePost = () => {
        if (confirm("Khachkar added successfully, do you want to add another one?")) {
            document.getElementById('add_khach_title').scrollIntoView();
        } else {
            window.location.href = `${base}/viewKhachkars/`;
        }
    }
</script>

<h1 id='add_khach_title' class='text-4xl font-bold'>Add Khachkar</h1>
<Form on:post_data={handlePost}/>