<script>
    import { onMount } from 'svelte';
    import { base } from '$app/paths';
    import { HOST, TEXT_FIELDS_NAMES, OPTION_FIELDS_NAMES } from '$lib/constants';
    import { Modal, Button, Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow } from 'flowbite-svelte';
    import ListIcon from '../components/icons/ListIcon.svelte';
    import SquareIcon from './icons/SquareIcon.svelte';
    import VideoIcon from '../components/icons/VideoIcon.svelte';
    export let entry_data;
    const FIELDS_NAMES = {...OPTION_FIELDS_NAMES, ...TEXT_FIELDS_NAMES, 'date': 'Upload date'};
    const FIELDS = Object.getOwnPropertyNames(FIELDS_NAMES);
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
    const previewData = async () => {
        clickOutsideModal = true;
    }
    let clickOutsideVideoModal = false;
    const previewVideo = async () => {
        clickOutsideVideoModal = true;
        await loadVideo();
    }
</script>

<div class='m-2 md:w-full flex flex-col border-b-2 border-amber-500 items-center w-auto'>
    <div class='p-4 md:flex md:justify-between md:max-h-[300px]'>
        <div class='m-2 flex flex-col justify-between items-center md:items-start'>
            <h1 class='text-4xl font-semibold'>{entry_data.location} {entry_data.id}</h1>
            <img class='max-h-[50vh] md:max-h-full rounded-lg md:rounded-none md:hidden w-full m-4 object-contain' src={image} alt={entry_data.id} />
            <p class='m-2'>{entry_data.inscription}</p>
            <p class="m-2 text-xs font-bold">Upload date {entry_data.date}</p>
            <div id='buttons_container' class='flex self-center'>
                <Button on:click={previewData} size="xs" class='m-2 bg-amber-500'>
                    <ListIcon sx='m-0 mr-1 text-white'/>
                    Preview Data
                </Button>
                {#if entry_data.state === 'processing_video'}
                    <Button disabled size="xs" class='m-2 bg-amber-500'>
                        <VideoIcon sx='m-0 mr-1 text-white'/>
                        Processing Khachkar video
                    </Button>
                {:else}
                    <Button on:click={previewVideo} size="xs" class='m-2 bg-amber-500'>
                        <VideoIcon sx='m-0 mr-1 text-white'/>
                        Preview Video
                    </Button>
                {/if}
                {#if entry_data.state === 'meshed' || entry_data.state === 'ready'}
                    <Button on:click={window.open(`${base}/viewMesh/${entry_data.id}`,'_blank','noopener')} size="xs" class='m-2 bg-amber-500'>
                        <SquareIcon sx='m-0 mr-1 text-white'/>
                        Preview Mesh
                    </Button>
                {/if}
            </div>
        </div>
        <img class='hidden md:block w-1/2 object-contain' src={image} alt={entry_data.id} />
    </div>
    <slot class='mx-auto'></slot>
</div>

<Modal title="Khachkar information" bind:open={clickOutsideModal} autoclose outsideclose>
    <Table striped={true}>
        <TableHead>
            <TableHeadCell>Field</TableHeadCell>
            <TableHeadCell>Value</TableHeadCell>
        </TableHead>
        <TableBody tableBodyClass="divide-y">
            {#each FIELDS as key}
                <TableBodyRow>
                    <TableBodyCell>{FIELDS_NAMES[key]}</TableBodyCell>
                    <TableBodyCell>{entry_data[key]}</TableBodyCell>
                </TableBodyRow>
            {/each}
        </TableBody>
    </Table>
    <svelte:fragment slot="footer">
        <Button color="alternative">Back</Button>
    </svelte:fragment>
</Modal>

<Modal title="video" bind:open={clickOutsideVideoModal} autoclose outsideclose>
    <video id="videoElement" controls class="w-full max-h-[100%]">
        <source type="video/mp4" id='videoDiv'>
        <track kind="captions">
        Your browser does not support the video tag.
    </video>
</Modal>