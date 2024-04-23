<script>
    import Entry from '../../components/Entry.svelte';
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    let entries = [];

    onMount(async () => {
        const response = await fetch(`${HOST}/get_khachkars/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        entries = await response.json();
        
    });

</script>

<h1 class='m-4 text-4xl font-bold'>Search Khachkars</h1>
<div class='flex flex-col items-center'>
    {#each entries.reverse() as entry}
        <Entry entry_data={entry} />
    {/each}
</div>
