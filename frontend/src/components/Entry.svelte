<script>
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { Modal, Button, Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow } from 'flowbite-svelte';
    export let entry_data;
    const text_fields = ['location', 'latLong', 'scenario', 'setting', 'landscape', 'accessibility', 'masters_name', 'category', 'production_period', 'motive', 'condition_of_preservation', 'inscription', 'important_features', 'backside', 'history_ownership', 'commemorative_activities', 'references', 'date']
    let image, video;

    onMount(async () => {
        const response = await fetch(`${HOST}/get_image/${entry_data.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `image/${entry_data.image}`
            }
        });
        image = URL.createObjectURL(await response.blob());
        console.log(entry_data.video);
        const vid_response = await fetch(`${HOST}/get_video/${entry_data.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': `video/${entry_data.video}`
            }
        });
        video = URL.createObjectURL(await vid_response.blob());
    });
    let clickOutsideModal = false;
    const previewData = () => {
        clickOutsideModal = true;
    }
</script>

<div class='m-4 p-8 bg-amber-300 flex justify-between max-h-[300px] md:w-[85%]'>
    <div class='flex flex-col justify-between'>
        <h1 class='text-4xl font-semibold'>{entry_data.location} {entry_data.id}</h1>
        <p class='m-2'>{entry_data.inscription}</p>
        <Button on:click={previewData} class='bg-amber-500'>Preview</Button>
        <p class="text-xs font-bold">Fecha {entry_data.date}</p>
    </div>
    <img class='w-1/2 object-contain' src={image} alt={entry_data.id} />
    <Modal title="Khachkar information" bind:open={clickOutsideModal} autoclose outsideclose>
        <video id="previewVideo" controls class="w-full h-auto">
            <source src={video} type="video/mp4">
            <track kind="captions">
            Your browser does not support the video tag.
        </video>
        <Table striped={true}>
            <TableHead>
                <TableHeadCell>Field</TableHeadCell>
                <TableHeadCell>Value</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each text_fields as key}
                    <TableBodyRow>
                        <TableBodyCell>{key}</TableBodyCell>
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