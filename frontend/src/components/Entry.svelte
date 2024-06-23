<script>
    import { onMount } from 'svelte';
    import { base } from '$app/paths';
    import { HOST, STATES_LABELS } from '$lib/constants';
    import { Modal, Button } from 'flowbite-svelte';
    import ListIcon from '../components/icons/ListIcon.svelte';
    import SquareIcon from './icons/SquareIcon.svelte';
    import VideoIcon from '../components/icons/VideoIcon.svelte';
    import KhachkarInfoModal from './KhachkarInfoModal.svelte';
    export let entry_data;
    export let target_id;
    let entryComponent;
    let componentID;
    let image;

    onMount(async () => {
        const response = await fetch(`${HOST}/get_image/${entry_data.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry_data.image}`
            }
        });
        let img_blob = await response.blob();
        if (img_blob.size > 0) 
            image = URL.createObjectURL(img_blob);
        else
            image = `${base}/images/no_thumb.jpg`;
        for (let key in entry_data) {
            if (entry_data[key] === null)
                entry_data[key] = "-"
        }
        entry_data.latLong = `${entry_data.latitude}, ${entry_data.longitude}`;

        // Scroll
        componentID = `entryComponent${entry_data.id}`;
        if (target_id !== null && target_id !== undefined && target_id !== '' && target_id === componentID) {
            setTimeout(() => {
                entryComponent.scrollIntoView(
                    {
                        behavior: 'smooth',
                        block: 'start',
                        inline: 'end'
                    }
                );
            }, 250);
        }
    });
    const loadVideo = async () => {
        if (entry_data.state === 'not_meshed' || entry_data.state === 'creating_mesh'){
            const response = await fetch(`${HOST}/get_video/${entry_data.id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': `video/${entry_data.video}`
                }
            });
            let preview = document.getElementById('videoDiv');
            preview.src = URL.createObjectURL(await response.blob());
            preview.onload = () => {
                URL.revokeObjectURL(preview.src) // free memory
            }
            let videoElement = document.getElementById('videoElement');
            videoElement.load();
        }
    }
    let clickOutsideModal = false;
    
    let clickOutsideVideoModal = false;
    const previewVideo = async () => {
        clickOutsideVideoModal = true;
        await loadVideo();
    }
</script>

<div bind:this={entryComponent} id={componentID} class='m-2 md:w-full flex flex-col border-b-2 border-amber-500 items-center w-auto scroll-smooth'>
    <div class='p-4 md:flex md:justify-between md:max-h-[300px] md:gap-2'>
        <div class='flex flex-col justify-between items-center md:items-start'>
            <h1 class='text-2xl font-semibold font-italic line-clamp-3 text-ellipsis'>{`${entry_data.id})`} {entry_data.location}</h1>
            <img class='max-h-[50vh] md:max-h-full rounded-lg md:rounded-none md:hidden w-full m-4 object-contain' src={image} alt={entry_data.id} />
            <p class='m-2'><b>Current state: </b>{STATES_LABELS[entry_data.state]}</p>
            <p class="m-2 text-xs font-bold">Upload date {entry_data.date}</p>
            <div id='buttons_container' class='w-full flex justify-between md:justify-start gap-2'>
                <Button on:click={async () => {clickOutsideModal = true;}} size="xs" class='w-full md:w-auto bg-amber-500'>
                    <ListIcon sx='m-0 mr-1 text-white'/>
                    Preview Data
                </Button>
                {#if entry_data.state === 'processing_video'}
                    <Button disabled size="xs" class='w-full md:w-auto bg-amber-500'>
                        <VideoIcon sx='m-0 mr-1 text-white'/>
                        Processing Khachkar video
                    </Button>
                {:else}
                    <Button on:click={previewVideo} size="xs" class='w-full md:w-auto bg-amber-500'>
                        <VideoIcon sx='m-0 mr-1 text-white'/>
                        Preview Video
                    </Button>
                {/if}
                {#if entry_data.state === 'meshed' || entry_data.state === 'ready'}
                    <Button on:click={window.open(`${base}/viewMesh/${entry_data.id}`,'_blank','noopener')} size="xs" class='w-full md:w-auto bg-amber-500'>
                        <SquareIcon sx='m-0 mr-1 text-white'/>
                        Preview Mesh
                    </Button>
                {/if}
            </div>
        </div>
        <img class='hidden md:block max-w-[40%] object-contain' src={image} alt={entry_data.id} />
    </div>
    <slot class='mx-auto'></slot>
</div>

<KhachkarInfoModal entry_data={entry_data} bind:clickOutsideModal={clickOutsideModal} />

<Modal title="video" bind:open={clickOutsideVideoModal} autoclose outsideclose>
    <video id="videoElement" controls class="w-full max-h-[100%]">
        <source type="video/mp4" id='videoDiv'>
        <track kind="captions">
        Your browser does not support the video tag.
    </video>
</Modal>