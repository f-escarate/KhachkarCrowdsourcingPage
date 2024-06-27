<script>
    import { Label, Button, Radio, Dropdown, Popover, Modal } from 'flowbite-svelte';
    import { BASE_MESH_DATA } from '$lib/constants';
    import { base } from '$app/paths';
    import DownIcon from '../icons/DownIcon.svelte';
    import VideoIcon from '../icons/VideoIcon.svelte';
    import SquareIcon from '../icons/SquareIcon.svelte';
    import QuestionIcon from '../icons/QuestionIcon.svelte';
    import ClipIcon from '../icons/ClipIcon.svelte';
    import VideoFileIcon from '../icons/VideoFileIcon.svelte';
    export let entry = {
        video: null
    };
    let videoVisibility = 0;
    let dropdownOpen = false;
    let modal = false;
    let meshData = {... BASE_MESH_DATA};
    const previewFile = (elementID, file) => {
        let preview = document.getElementById(elementID);
        preview.src = URL.createObjectURL(file);
        preview.onload = () => {
            URL.revokeObjectURL(preview.src) // free memory
        }
    }
    
    const loadVideo = (event) => {
        entry.video = event.target.files[0];
        previewFile('previewVideo', entry.video);
        let videoElement = document.getElementById('videoElement');
        videoElement.load();
        videoVisibility = 1;
    };

    const handleToggle = () => {
        if (!meshData.withMesh) 
            previewFile('previewVideo', entry.video);
    };

    export const restartData = () => {
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
        for (var key in meshData)
            meshData[key] = BASE_MESH_DATA[key];
    }
    export const validation = () => {
        let msg = '';
        if (entry.video == null && !meshData.withMesh)
            msg += 'Video cannot be empty\n';
        if (meshData.withMesh && (meshData.images.length == 0 || meshData.mesh == null || meshData.material == null))
            msg += 'Mesh files cannot be empty\n';
        return msg;
    }
    export const addMediaToRequest = (data, entry) => {
        data.append('video', entry.video);
        if (meshData.withMesh) {
            data.set('video', new File([''], 'fake.mp4', {type: 'video/mp4'}));
            data.append('mesh_files', meshData.mesh);
            data.append('mesh_files', meshData.material);
            for (let i = 0; i < meshData.images.length; i++)
                data.append('mesh_files', meshData.images[i]);
        } else {
            data.append('mesh_files', new File([''], 'fake.jpg', {type: 'image/jpeg'}));
        }
        return meshData.withMesh;
    }
</script>

<div class='flex flex-col w-full'>
    <div class='flex flex-col justify-start items-start gap-1'>   
        <div class='flex gap-1 items-center font-semibold h-full'>
            Select between Video or Mesh
            <div id='whatIsAMesh'>
                <QuestionIcon  sx='w-6 h-6 text-amber-500'/>
                <Popover class="w-64 text-sm " title="What is a mesh?" triggeredBy='#whatIsAMesh'>
                    A mesh is a representation of a 3D object. In this case is a 3D model of the khachkar.
                </Popover>
            </div>
        </div>     
        <Button class='bg-amber-500 hover:bg-amber-700 mb-4'>
            Selected: <p class='ml-1 font-bold'>{meshData.withMesh? 'Mesh': 'Video'}</p> <DownIcon sx='m-0 text-white'/>
        </Button>
        <Dropdown class="w-44 p-3 space-y-3 text-sm" bind:open={dropdownOpen}>
            <Radio class='p-1 rounded hover:bg-amber-200' name="wMesh" bind:group={meshData.withMesh} on:click={() => (dropdownOpen = false)} on:change={e => handleToggle()} value={false}>
                <VideoIcon sx='mx-1 text-black'/> Video
            </Radio>
            <Radio class='p-1 rounded hover:bg-amber-200' name="wMesh" bind:group={meshData.withMesh} on:click={() => (dropdownOpen = false)} on:change={e => handleToggle()} value={true}>
                <SquareIcon sx='mx-1 text-black'/> Mesh
            </Radio>
        </Dropdown>
    </div>
    {#if meshData.withMesh}
        <div class='inline-block mb-2 align-middle'>
            <SquareIcon sx='text-black inline'/>
            Upload a mesh
            <Button size="xs" class='bg-cyan-400 hover:bg-cyan-600 ml-2 my-auto' on:click={e => modal=true}>
                <p class='font-bold'>How to upload a mesh?</p>
            </Button>
        </div>
        <div class="mb-2 w-full flex flex-col gap-2">
            <label for="mesh" class='font-bold text-sm'>Mesh file (.obj)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.mesh=e.target.files[0]} id="mesh" name="mesh" accept=".obj">
            <label for="material" class='font-bold text-sm'>Material file (.mtl)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.material=e.target.files[0]} id="material" name="material" accept=".mtl">
            <label for="mesh_images" class='font-bold text-sm'>Texture files (multiple images)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.images=e.target.files} id="mesh_images" name="mesh_images" accept="image/*" multiple>
        </div>
        <Modal bind:open={modal} title='How to upload a mesh?' width='w-1/2' autoclose outsideclose>
            <p class='text'>To upload a mesh you need to have the following files:</p>
            <ul class='list-disc list-inside'>
                <li class='text-sm'>A .obj file that contains the 3D model.</li>
                <li class='text-sm'>A .mtl file that contains the material properties.</li>
                <li class='text-sm'>One or more image files that contain the textures.</li>
            </ul>
            <b class='text-amber-500'>Important: The images must be added all at once.</b>
            <img src={`${base}/gifs/gifUploadMesh.gif`} alt='Upload mesh example' class='w-full'/>
        </Modal>
    {:else}
        <p class='flex'><VideoFileIcon sx='w-6 h-6 text-black'/> Upload a video</p>
        <Label for="video" class="mb-2 w-full">
            <div class="rounded-xl my-4 p-1 flex border-4 border-amber-300 hover:bg-amber-500 hover:cursor-pointer text-center hover:text-white transition-colors duration-400 ease-in-out">
                <video class={(videoVisibility? 'visible': 'hidden') + ' md:w-1/2 m-auto p-2'} id='videoElement' controls>
                <source id="previewVideo">
                    <track kind="captions"/>
                    Your browser does not support HTML5 video.
                </video>
                <p class={(videoVisibility? 'hidden': 'visible') + ' self-center mx-auto inline-flex'}>
                    <ClipIcon sx='w-6 h-6'/>
                    Click to select a video...
                </p>
                <input type="file" id="video" name="video" class="w-0 invisible" on:change={loadVideo} accept="video/*">
            </div>
        </Label>
    {/if}
</div>

