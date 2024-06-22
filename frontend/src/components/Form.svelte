<script>
    import { createEventDispatcher } from 'svelte';
    import { Label, Button, Spinner } from 'flowbite-svelte';
    import { HOST, BASE_ENTRY } from '$lib/constants';
    import VideoOrMesh from './FormComponents/VideoOrMesh.svelte';
    import Metadata from './FormComponents/Metadata.svelte';
    import { auth_post_request } from '$lib/utils';
    
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar';
    export let button_text = 'Add Khachkar'
    export let entry = {... BASE_ENTRY};
    export let use_video_or_mesh = true;
    let metadataFieldsComponent;
    let videoOrMeshComponent;
    let isLoading = false;
    export const previewFile = (elementID, file) => {
        let preview = document.getElementById(elementID);
        preview.src = URL.createObjectURL(file);
        preview.onload = () => {
            URL.revokeObjectURL(preview.src) // free memory
        }
    }
    const dispatch = createEventDispatcher();
    function post_data_signal(){
        dispatch('post_data');
    }

    const restartForm = () => {
        if (use_video_or_mesh)
            videoOrMeshComponent.restartData();
        for (var key in entry)
            entry[key] = BASE_ENTRY[key];
    }
    const validation = () => {
        let msg = '';
        if (use_video_or_mesh)
            msg += videoOrMeshComponent.validation();
        if (msg !== '') {
            alert(msg);
            return false;
        }
        return true;
    }
    
    const handleSubmit = async (e) => {
        isLoading = true;
        if (!validation()) {
            isLoading = false;
            return;
        }
		const data = new FormData();
        if (!metadataFieldsComponent.addDataToRequest(data, entry)){
            isLoading = false;
            return;
        }
        data.append('image', entry.image);
        if (data.get('image') === "null")
            data.set('image', new File([''], 'fake.jpg', {type: 'image/jpeg'}));
        
        let formatted_endpoint = `${HOST}${endpoint_url}`;
        if (use_video_or_mesh){
            let withMesh = videoOrMeshComponent.addMediaToRequest(data, entry);
            formatted_endpoint = `${formatted_endpoint}/${+ withMesh}/`;
        }
        const response = await auth_post_request(formatted_endpoint, data, http_method);
        const json = await response.json();
        isLoading = false;
        if (json.status == 'success') {
            restartForm();
            post_data_signal();
        } else if (json.status == 'error'){
            alert('Failed to add: ' + json.msg);
        } else {
            alert('Failed to add (unknown reason)');
        }
    }
    const loadImage = (event) => {
        entry.image = event.target.files[0];
        previewFile('previewImage', entry.image);
    };

</script>

<div class='pt-5 grid gap-4 items-end w-full md:grid-cols-2'>
    <h2 class='md:col-span-2 text-2xl font-semibold'>Media</h2>
    <div class="my-2 md:flex md:flex-row gap-4 justify-between align-center md:col-span-2">
        {#if use_video_or_mesh}
            <VideoOrMesh bind:this={videoOrMeshComponent} {entry} />
        {/if}
        <div class='flex flex-col w-full self-end md:max-w-[50%]'>
            Upload image (optional)
            <Label for="image" class="mb-2 w-full md:bottom-0">
            <div class="my-4 p-1 flex border-4 border-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
                <img id="previewImage" class={(entry.image? 'visible': 'hidden') + " md:w-1/2 m-auto p-2"} alt="Thumbnail">
                <p class={(entry.image? 'hidden': 'visible') + ' self-center mx-auto'}>Upload Thumbnail</p>
                <input type="file" id="image" name="image" class="w-0 invisible" on:change={loadImage} accept="image/*">
            </div>
        </Label>
    </div>
    </div>
    <Metadata bind:this={metadataFieldsComponent} entry={entry}/>

    {#if isLoading}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500'>
            <Spinner class="mr-2" size="4"/>
            Loading...
        </Button>
    {:else}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit}>{button_text}</Button>
    {/if}
</div>