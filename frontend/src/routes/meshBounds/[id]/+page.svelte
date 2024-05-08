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
        current: {x: 0, y: 0, z: 0},
        max: {x: 0, y: 0, z: 0}   
    };
    const set_bounding_box_scales = (max_scales) => {
        bounding_box_scales.current = {...max_scales};
        bounding_box_scales.max = {...max_scales};
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
    const handleBoundingBox = (e) => {
        const { property, axis, value } = e.detail;
        bounding_box_scales[property][axis] = parseFloat(value);
        transform_bounding_box(bounding_box_scales.current);
    }
    const send_data = async (data, endpoint) => {
        isLoading = true;
        const response = await fetch(`${HOST}/${endpoint}/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: data
        });
        const res = await response.json();
        isLoading = false;
        if(res.status == 'success') {
            alert('Stone exported');
            location.reload();
        } else if (res.status == 'error') {
            alert('Error: ', res.msg);
        } else {
            alert('Unknown error');
        }
    }
    const send_bounding_box = async () => {
        let data = JSON.stringify(Object.values(bounding_box_scales.current));
        send_data(data, 'crop_mesh');
    }

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
    <Tabs style="underline">
        <TabItem open>
            <span slot="title">Box x</span>
            <RangeInput property='current' axis='x' interval={[0, bounding_box_scales.current.x, bounding_box_scales.max.x]} step={0.1} on:change={handleBoundingBox} />
        </TabItem>
        <TabItem>
            <span slot="title">Box y</span>
            <RangeInput property='current' axis='y' interval={[0, bounding_box_scales.current.y, bounding_box_scales.max.y]} step={0.1} on:change={handleBoundingBox} />
        </TabItem>
        <TabItem>
            <span slot="title">Box z</span>
            <RangeInput property='current' axis='z' interval={[0, bounding_box_scales.current.z, bounding_box_scales.max.z]} step={0.1} on:change={handleBoundingBox} />
        </TabItem>
    </Tabs>
    <div id='mesh_display' class='flex justify-center w-full'>
        <!-- Here goes the Three js display -->
    </div>
    <span id='tabs_bot_limit'></span>
    {#if isLoading}
        <Button disabled color="purple">
            <Spinner class="mr-2" size="4"/>
            Loading...
        </Button>
    {:else}
        <Button color="purple" on:click={send_bounding_box}>Crop mesh and save bounding box</Button>
    {/if}
</div>
