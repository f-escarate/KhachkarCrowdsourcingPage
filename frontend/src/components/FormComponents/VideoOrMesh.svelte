<script>
    import { Label, Toggle, Button, Radio, Dropdown } from 'flowbite-svelte';
    import DownIcon from '../icons/DownIcon.svelte';
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

    const handleToggle = () => {
        if (!meshData.withMesh) 
            previewFile('previewVideo', entry.video);
    };
</script>

<div class='flex flex-col w-full'>
    <div class='flex flex-col justify-start items-start gap-1'>   
        <p class='font-semibold h-full'>Select between Video or Mesh</p>     
        <Button class='bg-amber-500 hover:bg-amber-700 mb-4'>
            Selected: <p class='font-bold'>{meshData.withMesh? 'Mesh': 'Video'}</p> <DownIcon sx='m-0 text-white'/>
        </Button>
        <Dropdown class="w-44 p-3 space-y-3 text-sm">
            <Radio class='p-1 rounded hover:bg-amber-200' name="wMesh" bind:group={meshData.withMesh} on:change={e => handleToggle()} value={false}>
                <VideoIcon sx='mx-1 text-black'/> Video
            </Radio>
            <Radio class='p-1 rounded hover:bg-amber-200' name="wMesh" bind:group={meshData.withMesh} on:change={e => handleToggle()} value={true}>
                <SquareIcon sx='mx-1 text-black'/> Mesh
            </Radio>
        </Dropdown>
    </div>
    {#if meshData.withMesh}
        <p class='flex mb-2'>Upload mesh <SquareIcon sx='mx-1 text-black'/></p>
        <div class="mb-2 w-full flex flex-col gap-2">
            <label for="mesh" class='font-bold text-sm'>Mesh file (.obj)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.mesh=e.target.files[0]} id="mesh" name="mesh" accept=".obj">
            <label for="material" class='font-bold text-sm'>Material file (.mtl)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.material=e.target.files[0]} id="material" name="material" accept=".mtl">
            <label for="mesh_images" class='font-bold text-sm'>Texture files (multiple images)</label>
            <input type="file" class="mx-4 w-full" on:change={e => meshData.images=e.target.files} id="mesh_images" name="mesh_images" accept="image/*" multiple>
        </div>
    {:else}
        <p class='flex'>Upload video <VideoIcon sx='mx-1 text-black'/></p>
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

