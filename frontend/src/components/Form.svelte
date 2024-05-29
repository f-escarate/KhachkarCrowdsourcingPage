<script>
    import { createEventDispatcher } from 'svelte';
    import { FloatingLabelInput, Label, Button, Spinner } from 'flowbite-svelte';
    import { HOST, TEXT_FIELDS_NAMES, NUM_FIELDS_NAMES, OPTION_FIELDS_NAMES, BASE_ENTRY, BASE_MESH_DATA } from '$lib/constants';
    import VideoOrMesh from './FormComponents/VideoOrMesh.svelte';
    import SelectOptions from './FormComponents/SelectOptions.svelte';
    import { onMount } from 'svelte';
    import { auth_get_json } from '$lib/utils'
    
    export let token;
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar';
    export let button_text = 'Add Khachkar'
    export let videoVisibility = 0;
    export let entry = {... BASE_ENTRY};
    let meshData = {... BASE_MESH_DATA};
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
    let OPTION_FIELDS_OPTIONS_NAMES = {};
    let OPTION_FIELDS_OPTIONS_IDS = {};
    onMount(async () => {
        let response = await auth_get_json(`${HOST}/get_options_list/`, token);
        if (response.status != 200){
            alert('Failed to get options list, status code: ' + response.status);
            return;
        }
        response = await response.json();
        if (response.status === 'error') {
            alert('Failed to get options list: ' + response.msg);
        } else if (response.status === 'success') {
            for( var key in OPTION_FIELDS_NAMES ) {
                let options_list = response.msg[key];
                OPTION_FIELDS_OPTIONS_NAMES[key] = options_list.map((x) => x[0]);
                OPTION_FIELDS_OPTIONS_IDS[key] = options_list.map((x) => x[1]);
            }
        } else {
            alert('Failed to get options list (unknown reason)');
        }
    });

    const TEXT_FIELDS = Object.getOwnPropertyNames(TEXT_FIELDS_NAMES);
    const NUM_FIELDS = Object.getOwnPropertyNames(NUM_FIELDS_NAMES);
    const OPTION_FIELDS = Object.getOwnPropertyNames(OPTION_FIELDS_NAMES);
    const restartForm = () => {
        videoVisibility = 0;
        if (!meshData.withMesh){
            previewFile('previewVideo', new File([''], 'default.mp4', {type: 'video/mp4'}));
            let videoElement = document.getElementById('videoElement');
            videoElement.load();
        } else {
            document.getElementById('mesh').value = '';
            document.getElementById('material').value = '';
            document.getElementById('mesh_images').value = '';
        }
        for (var key in entry)
            entry[key] = BASE_ENTRY[key];
        for (var key in meshData)
            meshData[key] = BASE_MESH_DATA[key];
    }
    const validation = () => {
        let msg = '';
        if (entry.video == null && !meshData.withMesh)
            msg += 'Video cannot be empty\n';
        if (meshData.withMesh && (meshData.images.length == 0 || meshData.mesh == null || meshData.material == null))
            msg += 'Mesh files cannot be empty\n';
        
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
        for ( var field_name in OPTION_FIELDS_NAMES ) {
            let options_list = OPTION_FIELDS_OPTIONS_IDS[field_name];
            let option_index = entry[field_name];
            data.append(field_name, options_list[option_index]);
        }
        data.append('latitude', entry.latitude);
        data.append('longitude', entry.longitude);
        data.append('video', entry.video);
        data.append('image', entry.image);
        for ( var key in TEXT_FIELDS_NAMES ) {
            if (entry[key] !== null)
                data.append(key, entry[key]);
        }
            
        if (data.get('image') === "null")
            data.set('image', new File([''], 'fake.jpg', {type: 'image/jpeg'}));
        if (meshData.withMesh) {
            data.set('video', new File([''], 'fake.mp4', {type: 'video/mp4'}));
            data.append('mesh_files', meshData.mesh);
            data.append('mesh_files', meshData.material);
            for (let i = 0; i < meshData.images.length; i++)
                data.append('mesh_files', meshData.images[i]);
        } else {
            data.append('mesh_files', new File([''], 'fake.jpg', {type: 'image/jpeg'}));
        }
        const response = await fetch(`${HOST}${endpoint_url}/${+ meshData.withMesh}/`, {
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
        <VideoOrMesh bind:videoVisibility={videoVisibility} {entry} {meshData} />
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
    <h2 class='md:col-span-2 text-2xl font-semibold'>Metadata</h2>
    {#each OPTION_FIELDS as key}
        <SelectOptions title={OPTION_FIELDS_NAMES[key]} options={OPTION_FIELDS_OPTIONS_NAMES[key]} bind:value={entry[key]}/>
    {/each}
    {#each NUM_FIELDS as key}
        <FloatingLabelInput style="filled" type="number" name={key} id={key} label={NUM_FIELDS_NAMES[key]} bind:value={entry[key]}/>
    {/each}
    {#each TEXT_FIELDS as key}
        <FloatingLabelInput style="filled" type="text" name={key} id={key} label={TEXT_FIELDS_NAMES[key]} bind:value={entry[key]}/>
    {/each}
    

    {#if isLoading}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500'>
            <Spinner class="mr-2" size="4"/>
            Loading...
        </Button>
    {:else}
        <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit}>{button_text}</Button>
    {/if}
</div>