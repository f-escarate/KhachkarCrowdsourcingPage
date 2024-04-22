<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { Tabs, TabItem, Button, Spinner } from 'flowbite-svelte';
    import { init, animate, transform_stone, transform_camera } from '$lib/mesh_display';
    import { HOST } from '$lib/constants';
    import RangeInput from '../../../components/RangeInput.svelte';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let isLoading = false;
    let transformations = {
        pos: {x: 0, y: 0, z: 0},
        rot: {x: 0, y: 0, z: 0},
        scale: {value: 1}
    }
    let cam_props = {
        angle: 10,
        zoom: 75,
        height: 1
    }
    onMount(async () => {
        if(browser) {
            var mesh_display = document.getElementById('mesh_display');
            var mesh_display_rect = mesh_display.getBoundingClientRect()
            var tabs_bot = document.getElementById('tabs_bot_limit').getBoundingClientRect().bottom;
            let height = screen.height - tabs_bot;
            let width = mesh_display_rect.right-mesh_display_rect.left;
            init(width, height, mesh_display, id);
            animate()
	    }
    });

    const handleTransformations = (e) => {
        const { property, axis, value } = e.detail;
        transformations[property][axis] = parseFloat(value);
        transform_stone(transformations);
    }
    const handleCamera = (e) => {
        const { property, axis, value } = e.detail;
        cam_props[axis] = parseFloat(value);
        transform_camera(cam_props.angle, cam_props.zoom, cam_props.height);
    }
    const export_stone = async () => {
        isLoading = true;
        let data = JSON.stringify({
            pos: Object.values(transformations.pos),
            rot: Object.values(transformations.rot),
            scale: transformations.scale.value
        })
        const response = await fetch(`${HOST}/set_mesh_transformations/${id}/`, {
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
        } else if (res.status == 'error') {
            alert('Error exporting stone', res.msg);
        } else {
            alert('Unknown error exporting stone');
        }
    }

</script>

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
    <TabItem>
        <span slot="title">Camera control</span>
        <div class='flex'>
            <RangeInput property='' axis='angle' interval={[0, cam_props.angle, 360]} step={0.1} on:change={handleCamera} />
            <RangeInput property='' axis='zoom' interval={[0, cam_props.zoom, 100]} step={0.1} on:change={handleCamera} />
            <RangeInput property='' axis='height' interval={[-20, cam_props.height, 20]} step={0.1} on:change={handleCamera} />
        </div>
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

