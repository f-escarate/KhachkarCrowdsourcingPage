<script>
    import { Label, Toggle } from 'flowbite-svelte';
    export let videoVisibility = 'hidden';
    export let entry = {
        video: null
    };
    export let meshData = {
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
    
    const loadVideo = (event) => {
        entry.video = event.target.files[0];
        previewFile('previewVideo', entry.video);
        let videoElement = document.getElementById('videoElement');
        videoElement.load();
        videoVisibility = 'visible';
    };

    const loadMesh = (event) => {
        meshData.mesh = event.target.files[0];
    };
    const loadMaterial = (event) => {
        meshData.material = event.target.files[0];
    };
    const loadImages = (event) => {
        meshData.images = event.target.files;
    };
</script>

<div class='flex flex-col w-full'>
    <div class='flex justify-between'>
        Upload video or mesh
        <Toggle bind:checked={meshData.withMesh} label="Video or Mesh" />
    </div>
    {#if meshData.withMesh}
        <Label for="mesh" class="mb-2 w-full flex flex-col gap-2">
            Add mesh files (obj, mtl and images)
            <input type="file" on:change={loadMesh} id="mesh" name="mesh" class="w-full" accept=".obj">
            <input type="file" on:change={loadMaterial} id="material" name="material" class="w-full" accept=".mtl">
            <input type="file" on:change={loadImages} id="images" name="images" class="w-full" accept="image/*" multiple>
        </Label>
    {:else}
        <Label for="video" class="mb-2 w-full">
            Add video file
            <div class="my-4 p-1 flex bg-amber-300 hover:bg-amber-500 text-center hover:text-white transition-colors duration-400 ease-in-out">
                <video class={`md:w-1/2 m-auto p-2 ${videoVisibility}`} id='videoElement' controls>
                <source id="previewVideo">
                    <track kind="captions"/>
                    Your browser does not support HTML5 video.
                </video>
                <input type="file" id="video" name="video" class="w-0 invisible" on:change={loadVideo} accept=".mp4, .mov, .avi, .mkv, .wmv">
            </div>
        </Label>
    {/if}


</div>

