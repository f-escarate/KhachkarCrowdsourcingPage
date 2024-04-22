<script>
    import { onMount } from 'svelte';
    import { HOST, TEXT_FIELDS } from '$lib/constants';
    import { Modal, Button, Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow } from 'flowbite-svelte';
    export let entry_data;
    const FIELDS = Object.getOwnPropertyNames(TEXT_FIELDS);
    let image;

    onMount(async () => {
        const response = await fetch(`${HOST}/get_image/${entry_data.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry_data.image}`
            }
        });
        image = URL.createObjectURL(await response.blob());
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

<div class='m-4 p-4 md:p-8 bg-amber-300 md:flex md:justify-between md:max-h-[300px] md:w-[85%]'>
    <div class='flex flex-col justify-between items-center'>
        <h1 class='text-4xl font-semibold'>{entry_data.location} {entry_data.id}</h1>
        <img class='md:hidden w-full m-4 object-contain' src={image} alt={entry_data.id} />
        <p class='m-2'>{entry_data.inscription}</p>
        <div class='flex'>
            <Button on:click={previewData} size="xs" class='m-2 bg-amber-500'>Preview</Button>
            {#if entry_data.state === 'processing_video'}
                <h3>Khachkar video is being processed</h3>
            {:else if entry_data.state === 'meshed'}
                <h3>This Khachkar has been meshed</h3>
            {:else}
                <Button on:click={previewVideo} size="xs" class='m-2 bg-amber-500'>Video</Button>
                <Modal title="video" bind:open={clickOutsideVideoModal} autoclose outsideclose>
                    <video id="videoElement" controls class="w-full max-h-[100%]">
                        <source type="video/mp4" id='videoDiv'>
                        <track kind="captions">
                        Your browser does not support the video tag.
                    </video>
                </Modal>
            {/if}
        </div>
        
        <p class="text-xs font-bold">Upload date {entry_data.date}</p>
    </div>
    <img class='hidden md:block w-1/2 object-contain' src={image} alt={entry_data.id} />
    <Modal title="Khachkar information" bind:open={clickOutsideModal} autoclose outsideclose>
        <Table striped={true}>
            <TableHead>
                <TableHeadCell>Field</TableHeadCell>
                <TableHeadCell>Value</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each FIELDS as key}
                    <TableBodyRow>
                        <TableBodyCell>{TEXT_FIELDS[key]}</TableBodyCell>
                        <TableBodyCell>{entry_data[key]}</TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
        <svelte:fragment slot="footer">
            <Button color="alternative">Back</Button>
        </svelte:fragment>
    </Modal>
</div>