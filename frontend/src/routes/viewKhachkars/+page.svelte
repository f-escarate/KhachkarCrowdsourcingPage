<script>
    import Entry from '../../components/Entry.svelte';
    import EditIcon from '../../components/icons/EditIcon.svelte';
    import SquareIcon2 from '../../components/icons/SquareIcon2.svelte';
    import MagicIcon from '../../components/icons/MagicIcon.svelte';
    import { Button, Spinner } from 'flowbite-svelte'
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import { auth_get_json } from '$lib/utils';
    import Cookies from 'js-cookie';
    let entries = [];
    onMount(async () => {
        let token = await Cookies.get('token');
        if (token===undefined) {
            if(!alert("You have to be logged in to access this page")) {
                window.location.href = `${base}/login`;
            }
        }
        const response = await auth_get_json(`${HOST}/get_khachkars/`, Cookies.get('token'));
        entries = await response.json();
        entries.reverse();
    });
    async function handleKhachkarStateChange(e, entry_idx, endpoint, transition_state, final_state, error_state, ok_msg, error_msg) {
        let id = entries[entry_idx].id;
        entries[entry_idx].state = transition_state;
        const response = await auth_get_json(`${HOST}/${endpoint}/${id}/`, Cookies.get('token'));
        const json = await response.json();
        if (json.status === 'success') {
            entries[entry_idx].state = final_state;
            alert(ok_msg);
        } else if (json.status === 'error') {
            entries[entry_idx].state = error_state;
            alert(json.msg);
        } else {
            entries[entry_idx].state = error_state;
            alert(error_msg);
        }
    }
    const handleProcessMesh = async (e, entry_idx) => {
        await handleKhachkarStateChange(e, entry_idx, 'mesh_khachkar', 
            'creating_mesh', 'creating_mesh', 'not_meshed',
            'Meshing process started', 'Failed to mesh (unknown reason)'
        );
    }
    const setReady = async (e, index) => {
        await handleKhachkarStateChange(e, index, 'set_ready',
            'meshed', 'ready', 'meshed',
            'Khachkar set to ready', 'Failed to set ready (unknown reason)'
        );
    }
    const setUnready = async (e, index) => {
        await handleKhachkarStateChange(e, index, 'set_unready',
            'ready', 'meshed', 'ready',
            'Khachkar set to unready', 'Failed to set unready (unknown reason)'
        );
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
                    {#if entry.state === 'ready'}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-red-400 hover:bg-red-500' on:click={e => setUnready(e, i)}>
                            <SquareIcon2 sx='m-0 mr-1 text-white'/>
                            Set unready
                        </Button>
                    {:else if entry.state === 'meshed'}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-amber-600 hover:bg-amber-700' href={`${base}/meshTransformations/${entry.id}/`}>
                            <SquareIcon2 sx='m-0 mr-1 text-white'/>
                            Set mesh transformations
                        </Button>
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-green-400 hover:bg-green-500' on:click={e => setReady(e, i)}>
                            <SquareIcon2 sx='m-0 mr-1 text-white'/>
                            Set ready
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