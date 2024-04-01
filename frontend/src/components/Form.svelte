<script>
    import { FloatingLabelInput, Label, Button } from 'flowbite-svelte';
    import { HOST, TEXT_FIELDS_WO_DATE } from '$lib/constants';
    
    export let token;
    export let http_method = 'POST';
    export let endpoint_url = '/post_khachkar/';
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
        document.getElementById('previewImage').src = '';
        document.getElementById('previewVideo').src = '';
        videoElement.load();
        videoVisibility = 'hidden';
    }
    const validation = () => {
        let msg = '';
        if (entry.image == null)
            msg += 'Image cannot be empty\n';
        if (entry.video == null)
            msg += 'Video cannot be empty\n';
        
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
        for ( var key in entry ) {
            data.append(key, entry[key]);
        }
        const response = await fetch(`${HOST}${endpoint_url}`, {
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
        } else {
            alert('Failed to add');
        }
    }
    const loadImage = (event) => {
        entry.image = event.target.files[0];
        previewFile('previewImage', entry.image);
    };
    const loadVideo = (event) => {
        entry.video = event.target.files[0];
        previewFile('previewVideo', entry.video);
        let videoElement = document.getElementById('videoElement');
        videoElement.load();
        videoVisibility = 'visible';
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

        <Label for="video" class="mb-2 w-full">
        Upload video
        <div class="my-4 p-1 flex bg-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
            <video class={`md:w-1/2 m-auto p-2 ${videoVisibility}`} id='videoElement' controls>
            <source id="previewVideo">
                <track kind="captions"/>
                Your browser does not support HTML5 video.
            </video>
            <input type="file" id="video" name="video" class="w-0 invisible" on:change={loadVideo}>
        </div>
        </Label>
    </div>
    <Button class='md:col-span-2 w-[50%] mx-auto h-full text-black bg-amber-500' on:click={handleSubmit} pill>Add</Button>
</div>