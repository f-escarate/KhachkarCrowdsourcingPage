<script>
    import { Label, Toggle } from 'flowbite-svelte';
    import VideoIcon from '../icons/VideoIcon.svelte';
    import SquareIcon from '../icons/SquareIcon.svelte';

    export let videoVisibility = 0;
    export let entry = {
        video: null
    };
    export let meshData = {
        withMesh: false,
        mesh: null,
        material: null,
        images: []
    };
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

    const handleToggle = (event) => {
        if (!event.target.checked) 
            previewFile('previewVideo', entry.video);
    };
</script>

<div class='flex flex-col w-full'>
    <div class='flex justify-between'>
        Upload video or mesh
        <div class='flex justify-end'>
            <VideoIcon sx='m-0 mr-2 text-black'/>
            <Toggle bind:checked={meshData.withMesh} on:change={handleToggle} label="Video or Mesh" />
            <SquareIcon sx='m-0 text-black'/>
        </div>
    </div>
    {#if meshData.withMesh}
        <Label for="mesh" class="mb-2 w-full flex flex-col gap-2">
            Add mesh files (obj, mtl and images)
            <input type="file" class="w-full" on:change={e => meshData.mesh=e.target.files[0]} id="mesh" name="mesh" accept=".obj">
            <input type="file" class="w-full" on:change={e => meshData.material=e.target.files[0]} id="material" name="material" accept=".mtl">
            <input type="file" class="w-full" on:change={e => meshData.images=e.target.files} id="mesh_images" name="mesh_images" accept="image/*" multiple>
        </Label>
    {:else}
        <Label for="video" class="mb-2 w-full">
            <div class="my-4 p-1 flex border-4 border-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
                <video class={(videoVisibility? 'visible': 'hidden') + ' md:w-1/2 m-auto p-2'} id='videoElement' controls>
                <source id="previewVideo">
                    <track kind="captions"/>
                    Your browser does not support HTML5 video.
                </video>
                <p class={(videoVisibility? 'hidden': 'visible') + ' self-center mx-auto'}>Upload Video</p>
                <input type="file" id="video" name="video" class="w-0 invisible" on:change={loadVideo} accept="video/*">
            </div>
        </Label>
    {/if}   


</div>

