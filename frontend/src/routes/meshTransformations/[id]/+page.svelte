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
    let transformations = {
        pos: {x: 0, y: 0, z: 0},
        rot: {x: 0, y: 0, z: 0},
        scale: {value: 1}
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

    const handleTransformations = (e) => {
        const { property, axis, value } = e.detail;
        transformations[property][axis] = parseFloat(value);
        transform_stone(transformations);
    }
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

    const export_stone = async () => {
        let data = JSON.stringify({
            pos: Object.values(transformations.pos),
            rot: Object.values(transformations.rot),
            scale: transformations.scale.value
        })
        send_data(data, 'set_mesh_transformations');
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
        <TabItem open><span slot="title">Position x</span>
            <RangeInput property='pos' axis='x' interval={[-10, transformations.pos.x, 10]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem><span slot="title">Position y</span>
            <RangeInput property='pos' axis='y' interval={[-10, transformations.pos.y, 10]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem>
            <span slot="title">Position z</span>
            <RangeInput property='pos' axis='z' interval={[-10, transformations.pos.z, 10]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem>
            <span slot="title">Rotation x</span>
            <RangeInput property='rot' axis='x' interval={[-180, transformations.rot.x, 180]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem>
            <span slot="title">Rotation y</span>
            <RangeInput property='rot' axis='y' interval={[-180, transformations.rot.y, 180]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem>
            <span slot="title">Rotation z</span>
            <RangeInput property='rot' axis='z' interval={[-180, transformations.rot.z, 180]} step={0.1} on:change={handleTransformations} />
        </TabItem>
        <TabItem>
            <span slot="title">Scale</span>
            <RangeInput property='scale' axis='value' interval={[0, transformations.scale.value, 180]} step={0.1} on:change={handleTransformations} />
        </TabItem>
    </Tabs>
    <div id='mesh_display' class='flex justify-center w-full'>
        <!-- Here goes the Three js display -->
    </div>
    <span id='tabs_bot_limit'></span>
    {#if isLoading}
        <Button disabled>
            <Spinner class="mr-2" size="4"/>
            Loading...
        </Button>
    {:else}
        <Button on:click={export_stone}>Save stone transformations</Button>
    {/if}
</div>
