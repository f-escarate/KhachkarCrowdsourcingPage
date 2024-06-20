<script>
    import Entry from '../../components/Entry.svelte';
    import EditIcon from '../../components/icons/EditIcon.svelte';
    import SquareIcon2 from '../../components/icons/SquareIcon2.svelte';
    import MagicIcon from '../../components/icons/MagicIcon.svelte';
    import DownIcon from '../../components/icons/DownIcon.svelte';
    import ClockIcon from '../../components/icons/ClockIcon.svelte';
    import { Button, Spinner, Checkbox, Dropdown, Radio } from 'flowbite-svelte'
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    import { auth_get_json, get_json } from '$lib/utils';
    import Cookies from 'js-cookie';
    let entries = null;
    let filtered_entries = [];
    let user_id = null;
    let only_my_khachkars = false;
    let khachkars_state = 'all';

    onMount(async () => {
        const khachkars_response = await get_json(`${HOST}/get_khachkars/`);
        entries = await khachkars_response.json();
        entries.reverse();

        let token = Cookies.get('token');
        if (token !== undefined) {
            const user_response = await auth_get_json(`${HOST}/get_user_id/`, token);
            if (user_response.status === 200) {
                let data = await user_response.json()
                user_id = await data.user_id;
            }
        }
        
        filter_khachkars();
        
    });

    const filter_khachkars = () => {
        filtered_entries = [...entries];
        if (only_my_khachkars && user_id !== null)
            for (let i = entries.length - 1; i >= 0; i--)
                if (entries[i].owner_id !== user_id)
                    filtered_entries.splice(i, 1);
        if (khachkars_state !== 'all')
            for (let i = filtered_entries.length - 1; i >= 0; i--)
                if (filtered_entries[i].state !== khachkars_state)
                    filtered_entries.splice(i, 1);
    }

    async function handleKhachkarStateChange(e, entry_idx, endpoint, transition_state, final_state, error_state, ok_msg, error_msg) {
        let id = filtered_entries[entry_idx].id;
        filtered_entries[entry_idx].state = transition_state;
        const response = await auth_get_json(`${HOST}/${endpoint}/${id}/`, Cookies.get('token'));
        const json = await response.json();
        if (json.status === 'success') {
            filtered_entries[entry_idx].state = final_state;
            alert(ok_msg);
        } else if (json.status === 'error') {
            filtered_entries[entry_idx].state = error_state;
            alert(json.msg);
        } else {
            filtered_entries[entry_idx].state = error_state;
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

<div class='flex flex-col items-center md:max-w-[80%] md:mx-auto self-center'>
    <div class='m-2 flex self-start w-full items-center gap-4'>
        <Button class='bg-amber-500 hover:bg-amber-700'>
            Filter by Khachkar state <DownIcon sx='m-0 text-white'/>
        </Button>
        <Dropdown class="w-44 p-3 space-y-3 text-sm">
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'all'}>All</Radio>
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'processing_video'}>Processing video</Radio>
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'not_meshed'}>Not meshed</Radio>
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'creating_mesh'}>Creating mesh</Radio>
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'meshed'}>Meshed</Radio>
            <Radio name="khachkars_state" bind:group={khachkars_state} on:change={e=> filter_khachkars()} value={'ready'}>Ready</Radio>
        </Dropdown>
        {#if user_id !== null}
            <Checkbox class='bg-amber-500 hover:bg-amber-700 h-full p-3 rounded-lg' bind:checked={only_my_khachkars} on:change={e => filter_khachkars()} color='orange'>
                <p class='text-white'>Show my khachkars only</p>
            </Checkbox>
        {:else}
            <a href={`${base}/enter/login`} class='font-semibold underline text-amber-600'>Login to manage your khachkars</a>
        {/if}
    
    </div>
    {#if entries === null}
        <Spinner class='m-4' size='10'/> <h1 class='text-2xl font-bold'>Loading khachkars</h1>
    {:else if filtered_entries.length > 0}
        {#if user_id !== null}
            {#each filtered_entries as entry, i}
            <Entry entry_data={entry}>
                {#if entry.owner_id === user_id}
                <div class='md:mt-2 mb-4 px-4 flex flex-col md:flex-row md:justify-between md:max-h-[300px] w-full gap-4'>
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
                    {:else if entry.state === 'queued_for_meshing'}
                    <Button disabled class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-purple-500 hover:bg-purple-700'>
                        <ClockIcon sx='m-0 mr-1 text-white'/>
                        Queued for meshing
                    </Button>
                    {:else if entry.state === 'not_meshed'}
                        <Button class='md:col-span-2 w-full md:w-[50%] mx-auto h-full bg-purple-500 hover:bg-purple-700' on:click={e => handleProcessMesh(e, i)}>
                            <MagicIcon sx='m-0 mr-1 text-white'/>
                            Process mesh
                        </Button>
                    {/if}
                </div>
                {/if}
            </Entry>
            {/each}
        {:else}
            {#each filtered_entries as entry, i}
                <Entry entry_data={entry}/>                
            {/each}
        {/if}
    {:else}
        <h1 class='text-4xl font-bold'>No entry found</h1>
    {/if}
</div>