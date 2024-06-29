<script>
    import Form from '../../components/Form.svelte';
    import { base } from "$app/paths";
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';
    let formComponent;
    onMount(() => {
        if (Cookies.get('access_token')===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/enter/login`;
            }
        }
    });
    const handlePost = () => {
        formComponent.confirmationModal(
            'Khachkar added successfully',
            'Do you want to add another one?',
            () => {document.getElementById('add_khach_title').scrollIntoView();},
            () => {window.location.href = `${base}/viewKhachkars/`;},
            true
        );
    }
</script>

<h1 id='add_khach_title' class='text-4xl font-bold'>Add Khachkar</h1>
<Form bind:this={formComponent} on:post_data={handlePost}/>