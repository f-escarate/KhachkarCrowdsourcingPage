<script>
    import { FloatingLabelInput, Label, Button } from 'flowbite-svelte';
    import { HOST, TEXT_FIELDS_WO_DATE } from '$lib/constants';
    import VideoOrMesh from './FormComponents/VideoOrMesh.svelte';
    
    export let token;
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar';
    export let videoVisibility = 'hidden';
    export let entry = {
        location: '',
        latLong: '',
        scenario: '',
        setting: '',
        landscape: '',
        accessibility: '',
        masters_name: '',
        category: '',
        production_period: '',
        motive: '',
        condition_of_preservation: '',
        inscription: '',
        important_features: '',
        backside: '',
        history_ownership: '',
        commemorative_activities: '',
        references: '',
        image : null,
        video: null,
    };
    let meshData = {
        withMesh: false,
        mesh: null,
        material: null,
        images: []
    };
    export const previewFile = (elementID, file) => {
        let preview = document.getElementById(elementID);
        preview.src = URL.createObjectURL(file);
        preview.onload = () => {
            URL.revokeObjectURL(preview.src) // free memory
        }
    }
    const FIELDS = Object.getOwnPropertyNames(TEXT_FIELDS_WO_DATE);
    const restartForm = () => {
        entry.location = '';
        entry.latLong = '';
        entry.scenario = '';
        entry.setting = '';
        entry.landscape = '';
        entry.accessibility = '';
        entry.masters_name = '';
        entry.category = '';
        entry.production_period = '';
        entry.motive = '';
        entry.condition_of_preservation = '';
        entry.inscription = '';
        entry.important_features = '';
        entry.backside = '';
        entry.history_ownership = '';
        entry.commemorative_activities = '';
        entry.references = '';
        entry.image = null;
        entry.video = null;
        meshData.mesh = null;
        meshData.material = null;
        meshData.images = [];
        document.getElementById('previewImage').src = '';
        if (!meshData.withMesh){
            let videoElement = document.getElementById('videoElement');
            videoElement.src = '';
            videoElement.load();
        } else {
            document.getElementById('mesh').value = '';
            document.getElementById('material').value = '';
            document.getElementById('mesh_images').value = '';
        }
        videoVisibility = 'hidden';
    }
    const validation = () => {
        let msg = '';
        if (entry.image == null)
            entry.image = new File([''], 'default.jpg', {type: 'image/jpeg'});
        if (entry.video == null && !meshData.withMesh)
            msg += 'Video cannot be empty\n';
        else if (entry.video == null)
            entry.video = new File([''], 'default.mp4', {type: 'video/mp4'});
        if (meshData.withMesh && (meshData.images.length == 0 || meshData.mesh == null || meshData.material == null))
            msg += 'Mesh files cannot be empty\n';
        
        if (msg !== '') {
            alert(msg);
            return false;
        }
        return true;
    }
    
    const handleSubmit = async (e) => {
        if (!validation()) {
            return;
        }
		const data = new FormData();
        for ( var key in entry ) 
            data.append(key, entry[key]);
        if (meshData.withMesh) {
            data.append('mesh_files', meshData.mesh);
            data.append('mesh_files', meshData.material);
            for (let i = 0; i < meshData.images.length; i++) {
                data.append('mesh_files', meshData.images[i]);
            }
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
        if (json.status == 'success') {
            alert('Successfully added');
            restartForm();
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
    {#each FIELDS as key}
        <FloatingLabelInput style="filled" type="text" name={key} id={key} label={TEXT_FIELDS_WO_DATE[key]} bind:value={entry[key]}/>
    {/each}

    <div class="my-2 md:flex md:flex-row gap-4 justify-between align-center md:col-span-2">
        <Label for="image" class="mb-2 w-full">
        Upload image
        <div class="my-4 p-1 flex bg-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
            <img id="previewImage" class="md:w-1/2 m-auto p-2" alt="Thumbnail">
            <input type="file" id="image" name="image" class="w-0 invisible" on:change={loadImage}>
        </div>
        </Label>

        <VideoOrMesh {videoVisibility} {entry} {meshData} {previewFile} />
    </div>
    <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit} pill>Add</Button>
</div>