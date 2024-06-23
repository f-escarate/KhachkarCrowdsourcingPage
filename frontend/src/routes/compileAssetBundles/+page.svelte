<script>
    import { onMount } from 'svelte';
    import { Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow, Checkbox, Button, Spinner } from 'flowbite-svelte';
    import KhachkarInfoModal from '../../components/KhachkarInfoModal.svelte'
    import EyeIcon from '../../components/icons/EyeIcon.svelte';
    import ListIcon from '../../components/icons/ListIcon.svelte';
    import SquareIcon from '../../components/icons/SquareIcon.svelte';
    import ForwardIcon from '../../components/icons/ForwardIcon.svelte';
    import { HOST } from '$lib/constants';
    import { base } from '$app/paths';
    import { auth_get_json, auth_post_request } from '$lib/utils';
    import Cookies from 'js-cookie';
    let entries = [];
    let khachkars_in_unity = [];
    let compiling_asset_bundles = false;
    onMount(async () => {
        if (Cookies.get('access_token')===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/enter/login`;
            }
        }
        const response = await auth_get_json(`${HOST}/get_khachkars/ready/`);
        entries = await response.json();
        const response2 = await auth_get_json(`${HOST}/get_khachkars_in_unity/`);
        khachkars_in_unity = await response2.json();
        if (khachkars_in_unity.status !== 'success') {
            alert('Failed to get the list of khachkars that are currently in the Museum');
            return;
        }
        khachkars_in_unity = khachkars_in_unity.khachkars;
        let checkboxes = document.getElementsByName('checkbox');
        for (let i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = khachkars_in_unity.includes(entries[i]['id']);
        }
    });
    const handleCompilation = async () => {
        if (!confirm("Are you sure you want to compile asset bundles?"))
            return;
        compiling_asset_bundles = true;
        let khachkar_ids = [];
        let checkboxes = document.getElementsByName('checkbox');
        for (let i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                khachkar_ids.push(entries[i]['id']);
            }
        }
        const response = await auth_post_request(`${HOST}/compile_asset_bundles/`, JSON.stringify(khachkar_ids), 'POST', true);
        let msg = await response.json();
        if (msg.status === 'success') {
            alert("Asset bundles have been compiled successfully");
        } else {
            alert(msg.msg);
        }
        compiling_asset_bundles = false;
    }
    const handleSelectAll = (e) => {
        let checkboxes = document.getElementsByName('checkbox');
        for (let i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = e.target.checked;
        }
    }
    let clickOutsideModal = false;
    let entry_data = {};
</script>

<KhachkarInfoModal entry_data={entry_data} bind:clickOutsideModal={clickOutsideModal} />
<h1 class='text-4xl font-bold'>Manage khachkars in the museum</h1>
<div class='flex flex-col'>
    {#if entries.length > 0}
        <h2 class='my-2 text-xl font-semibold text-amber-600'>Khachkars to add </h2>
        <Table striped={true} shadow={true} class='border-4 border-amber-400 rounded-lg'>
            <TableHead theadClass='text-xs uppercase align-text-top'>
                <TableHeadCell padding='px-3 py-3'>Khachkar</TableHeadCell> 
                <TableHeadCell padding='px-1 py-3'><EyeIcon sx="inline mr-1"/>View info</TableHeadCell>
                <TableHeadCell padding='px-1 py-3'><EyeIcon sx="inline mr-1"/>View mesh</TableHeadCell>
                <TableHeadCell padding='px-3 py-3' class='h-full align-middle'>
                    <Checkbox inline on:click={handleSelectAll}>
                        <p class='text-xs uppercase align-text-top font-bold'>Select all</p>
                    </Checkbox>
                </TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each entries as entry}
                    <TableBodyRow>
                        <TableBodyCell tdClass='px-3 py-4 font-medium'>
                            {`${entry['id']}) ${entry['location']}`}
                            <a class='inline underline text-amber-700 text-bold italic'
                                href={`${base}/viewKhachkars#entryComponent${entry.id}`}
                                target="_blank" rel="noopener"
                                >
                                Go
                                <ForwardIcon sx='text-amber-700 inline'/>
                            </a>
                        </TableBodyCell>
                        <TableBodyCell tdClass='px-1 py-4'>
                            <Button on:click={async () => {clickOutsideModal = true; entry_data=entry;}} size="xs" class='w-full bg-amber-500'>
                                <ListIcon sx='text-white'/>
                            </Button>
                        </TableBodyCell>
                        <TableBodyCell tdClass='px-1 py-4'>
                            <Button on:click={window.open(`${base}/viewMesh/${entry.id}`,'_blank','noopener')} size="xs" class='w-full bg-orange-500'>
                                <SquareIcon sx='text-white'/>
                            </Button>
                        </TableBodyCell>
                        <TableBodyCell tdClass='px-3 py-4'>
                            <Checkbox name='checkbox'/>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
        {#if compiling_asset_bundles}
            <p class='m-2 font-bold text-orange-700'>This process could take a few minutes</p>
            <Button disabled class='self-end max-w-[400px] my-4 bg-amber-500'>
                <Spinner class="mr-2" size="4"/>
                Compiling asset bundles...
            </Button>
        {:else}
            <Button on:click={handleCompilation} class='self-end max-w-[400px] my-4 bg-amber-500'>
                Add selected khachkars to the museum
            </Button>
        {/if}
        
    {:else}
        <h2 class='m-4'>No entries found</h2>
    {/if}
</div>
