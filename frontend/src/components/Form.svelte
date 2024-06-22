<script>
    import { createEventDispatcher } from 'svelte';
    import { Label, Button, Spinner } from 'flowbite-svelte';
    import { HOST, BASE_ENTRY } from '$lib/constants';
    import VideoOrMesh from './FormComponents/VideoOrMesh.svelte';
    import Metadata from './FormComponents/Metadata.svelte';
    
    export let token;
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar';
    export let button_text = 'Add Khachkar'
    export let videoVisibility = 0;
    export let entry = {... BASE_ENTRY};
    let metadata_fields_component;
    let videoOrMeshSlot;
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
        videoOrMeshSlot.restartData();
        for (var key in entry)
            entry[key] = BASE_ENTRY[key];
    }
    const validation = () => {
        let msg = '';
        msg += videoOrMeshSlot.validation();
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
        if (!metadata_fields_component.addDataToRequest(data, entry)){
            isLoading = false;
            return;
        }
        data.append('image', entry.image);
        if (data.get('image') === "null")
            data.set('image', new File([''], 'fake.jpg', {type: 'image/jpeg'}));
        
        let withMesh = videoOrMeshSlot.addMediaToRequest(data, entry)
        
        const response = await fetch(`${HOST}${endpoint_url}/${+ withMesh}/`, {
            method: http_method,
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: data
        });
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
        <VideoOrMesh bind:this={videoOrMeshSlot} bind:videoVisibility={videoVisibility} {entry} />
        <div class='flex flex-col w-full self-end'>
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
    <Metadata bind:this={metadata_fields_component} entry={entry}/>

    {#if isLoading}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500'>
            <Spinner class="mr-2" size="4"/>
            Loading...
        </Button>
    {:else}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit}>{button_text}</Button>
    {/if}
</div>