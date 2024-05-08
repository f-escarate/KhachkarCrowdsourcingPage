<script>
    import Entry from '../../components/Entry.svelte';
    import EditIcon from '../../components/icons/EditIcon.svelte';
    import SquareIcon2 from '../../components/icons/SquareIcon2.svelte';
    import MagicIcon from '../../components/icons/MagicIcon.svelte';
    import { Button, Spinner } from 'flowbite-svelte'
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import Cookies from 'js-cookie';
    let entries = [];
    onMount(async () => {
        let token = await Cookies.get('token');
        if (token===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/login`;
            }
        }
        const response = await fetch(`${HOST}/get_khachkars/own/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Cookies.get('token')}`
            }
        });
        entries = await response.json();
        entries.reverse();
    });
    const handleProcessMesh = async (e, entry_idx) => {
        let id = entries[entry_idx].id;
        entries[entry_idx].state = 'creating_mesh';
        const response = await fetch(`${HOST}/mesh_khachkar/${id}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Cookies.get('token')}`
            }
        });
        const json = await response.json();
        if (json.status === 'success') {
            alert("Meshing process started");
        } else if (json.status === 'error') {
            entries[entry_idx].state = 'not_meshed';
            alert(json.msg);
        } else {
            entries[entry_idx].state = 'not_meshed';
            alert('Failed to mesh (unknown reason)');
        }
    }

</script>

<h1 class='m-4 text-4xl font-bold'>Your Khachkars</h1>
<div class='flex flex-col items-center'>
    {#if entries.length > 0}
        {#each entries as entry, i}
            <Entry entry_data={entry}>
                <div class='m-4 flex flex-col md:flex-row md:justify-between md:max-h-[300px] md:w-[85%] gap-4'>
                    <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-cyan-500 hover:bg-cyan-600' href={`${base}/editEntry/${entry.id}/`}>
                        <EditIcon sx='m-0 mr-1 text-white'/>
                        Edit entry
                    </Button>
                    {#if entry.state === 'meshed'}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-amber-600 hover:bg-amber-700' href={`${base}/meshTransformations/${entry.id}/`}>
                            <SquareIcon2 sx='m-0 mr-1 text-white'/>
                            Set mesh transformations
                        </Button>
                    {:else if entry.state === 'creating_mesh'}
                    <Button disabled class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-purple-500 hover:bg-purple-700'>
                        <Spinner class="mr-2" size="5"/>
                        Generating mesh
                    </Button>
                    {:else if entry.state === 'not_meshed'}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-purple-500 hover:bg-purple-700' on:click={e => handleProcessMesh(e, i)}>
                            <MagicIcon sx='m-0 mr-1 text-white'/>
                            Process mesh
                        </Button>
                    {/if}
                </div>
            </Entry>
        {/each}
    {:else}
        <h1 class='text-4xl font-bold'>No entry found :c</h1>
    {/if}
</div>