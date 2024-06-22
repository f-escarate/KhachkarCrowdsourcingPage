<script>
    import { onMount } from 'svelte';
    import { Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow, Checkbox, Button, Spinner } from 'flowbite-svelte';
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


</script>

<h1 class='m-4 text-4xl font-bold'>Compile Asset Bundles</h1>
<div class='flex flex-col'>
    {#if entries.length > 0}
        <Table striped={true}>
            <TableHead>
                <TableHeadCell>Khachkar</TableHeadCell> 
                <TableBodyCell><Checkbox on:click={handleSelectAll} /></TableBodyCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each entries as entry}
                    <TableBodyRow>
                        <TableBodyCell>{entry['location']} {entry['id']}</TableBodyCell>
                        <TableBodyCell><Checkbox name='checkbox' /></TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
        {#if compiling_asset_bundles}
            <p class='m-2 font-bold text-orange-700'>This process could take a few minutes</p>
            <Button disabled size="xs" class='m-2 bg-amber-500'>
                <Spinner class="mr-2" size="4"/>
                Compiling asset bundles...
            </Button>
            
        {:else}
            <Button on:click={handleCompilation} size="xs" class='m-2 bg-amber-500'>Compile Asset Bundles</Button>
        {/if}
        
    {:else}
        <p class='m-4'>No entries found</p>
    {/if}
</div>
