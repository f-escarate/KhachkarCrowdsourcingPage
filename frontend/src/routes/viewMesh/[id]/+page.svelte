<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { Tabs, TabItem, Button, Spinner, Progressbar } from 'flowbite-svelte';
    import { init, animate, transform_stone, transform_bounding_box } from '$lib/mesh_display';
    import { HOST } from '$lib/constants';
    import RangeInput from '../../../components/RangeInput.svelte';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let isLoading = false;
    const progress_obj = {
        loaded: false,
        progress: 0
    };
    const set_progress = (p, b) => {
        progress_obj.progress = p;
        progress_obj.loaded = b;
    };
    let bounding_box_scales = {
        current: {x: 0, y: 0, z: 0}
    };
    const set_bounding_box_scales = (max_scales) => {
        bounding_box_scales.current = {...max_scales};
        transform_bounding_box(bounding_box_scales.current);
    };
    
    onMount(async () => {
        if(browser) {
            var mesh_display = document.getElementById('mesh_display');
            var mesh_display_rect = mesh_display.getBoundingClientRect()
            var tabs_bot = document.getElementById('tabs_bot_limit').getBoundingClientRect().bottom;
            let height = screen.height - tabs_bot;
            let width = mesh_display_rect.right-mesh_display_rect.left;
            init(width, height, mesh_display, id, set_progress, set_bounding_box_scales);
            animate()
	    }
    });
</script>

<div class={(progress_obj.loaded? 'hidden': 'visible')}>
    <h1 class="text-3xl font-bold text-center">Loading Mesh...</h1>
    <Progressbar 
        progress={progress_obj.progress} 
        size="h-10" labelInside color="green" 
        labelInsideClass="text-white text-2xl font-medium text-center p-2 rounded-full" 
        class="my-4"
    />
</div>

<div class={(progress_obj.loaded? 'visible': 'invisible')}>
    <span id='tabs_top_limit' class='w-full'></span>
    <div id='mesh_display' class='flex justify-center w-full'>
        <!-- Here goes the Three js display -->
    </div>
    <span id='tabs_bot_limit'></span>
</div>
