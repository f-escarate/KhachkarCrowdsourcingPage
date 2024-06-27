<script>
    import { Modal, Button, Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow } from 'flowbite-svelte';
    import { TEXT_FIELDS_NAMES, OPTION_FIELDS_NAMES } from '$lib/constants';
    import EditIcon from './icons/EditIcon.svelte';
    import CloseIcon from './icons/CloseIcon.svelte';
    export let entry_data;
    export let clickOutsideModal = false;
    
    const FIELDS_NAMES = {
        ...OPTION_FIELDS_NAMES,
        ...TEXT_FIELDS_NAMES,
        latLong: 'Latitude and Longitude',
        'date': 'Upload date'
    };
    const FIELDS = Object.getOwnPropertyNames(FIELDS_NAMES);
</script>

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
        <Button class='bg-red-500 hover:bg-red-700'>
            <CloseIcon sx='m-0 mr-1 text-white'/>
            Back
        </Button>
        <Button class="bg-cyan-500 hover:bg-cyan-700">
            <EditIcon sx='m-0 mr-1 text-white'/>
            Edit data or image
        </Button>
    </svelte:fragment>
</Modal>