<script>
    import { onMount } from 'svelte';
    import { Table, TableBody, TableHead, TableBodyCell, TableHeadCell, TableBodyRow, Checkbox, Button } from 'flowbite-svelte';
    import { HOST } from '$lib/constants';
    import { base } from '$app/paths';
    import Cookies from 'js-cookie';
    let entries = [];
    let token;
    onMount(async () => {
        token = Cookies.get('token');
        if (token===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/login`;
            }
        }
        const response = await fetch(`${HOST}/get_khachkars/mesh/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        entries = await response.json();
    });
    const handleCompilation = async () => {
        if (!confirm("Are you sure you want to compile asset bundles?"))
            return;
        
        const response = await fetch(`${HOST}/compile_asset_bundles/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token || ''
            }
        });
        let msg = await response.json();
        if (msg.status === 'success') {
            alert("Asset bundles have been compiled successfully");
        } else {
            alert("An error occurred while compiling asset bundles");
        }
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
        <Button on:click={handleCompilation} size="xs" class='m-2 bg-amber-500'>Compile Asset Bundles</Button>
    {:else}
        <p class='m-4'>No entries found</p>
    {/if}
</div>
