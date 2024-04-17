<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { init, animate } from '$lib/mesh_display';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id

    onMount(async () => {
        if(browser) {
            init(window, document.getElementById('mesh_display'));
            animate()
	    }
    });
</script>


<section>
	Hello World.
</section>
<h1>id</h1>
<div id='mesh_display'>

</div>