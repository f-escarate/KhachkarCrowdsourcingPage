<script>
    import Entry from '../../components/Entry.svelte';
    import { Button, Spinner } from 'flowbite-svelte'
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import Cookies from 'js-cookie';
    let entries = [];
    let isLoading = false;
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
        
    });
    const handleProcessMesh = async (e, entry) => {
        let id = entry.id;
        isLoading = true;
        const response = await fetch(`${HOST}/mesh_khachkar/${id}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Cookies.get('token')}`
            }
        });
        const json = await response.json();
        isLoading = false;
        if (json.status === 'success') {
            entry.state = 'creating_mesh';
            alert("Meshing process started");
        } else if (json.status === 'error') {
            entry.state = 'not_meshed';
            alert(json.msg);
        } else {
            entry.state = 'not_meshed';
            alert('Failed to mesh (unknown reason)');
        }
    }

</script>

<div class='flex flex-col items-center'>
    {#if entries.length > 0}
        <h1 class='text-4xl font-bold'>Your Khachkars</h1>
        {#each entries.reverse() as entry}
            <Entry entry_data={entry} />
            <div class='m-4 flex flex-col md:flex-row md:justify-between md:max-h-[300px] md:w-[85%] gap-4'>
                <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full' color="blue" href={`${base}/editEntry/${entry.id}/`}>Edit entry</Button>
                {#if entry.state === 'meshed'}
                    <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full' color="blue" href={`${base}/viewMesh/${entry.id}/`}>View mesh</Button>
                {:else if entry.state === 'creating_mesh'}
                    <h3>Khachkar mesh in progress...</h3>
                {:else if entry.state === 'not_meshed'}
                    {#if isLoading}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full' color="blue">
                            <Spinner class="mr-2" size="4"/>
                            Processing mesh
                        </Button>
                    {:else}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full' color="blue" on:click={e => handleProcessMesh(e, entry)}>
                            Process mesh
                        </Button>
                    {/if}
                {/if}
            </div>
        {/each}
    {:else}
        <h1 class='text-4xl font-bold'>No entry found :c</h1>
    {/if}
</div>