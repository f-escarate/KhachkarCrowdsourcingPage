<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { Tabs, TabItem } from 'flowbite-svelte';
    import { init, animate, transform_stone } from '$lib/mesh_display';
    import RangeInput from '../../../components/RangeInput.svelte';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let transformations = {
        pos: {x: 0, y: 0, z: 0},
        rot: {x: 0, y: 0, z: 0},
        scale: {value: 1}
    }
    onMount(async () => {
        if(browser) {
            var mesh_display = document.getElementById('mesh_display');
            var mesh_display_rect = mesh_display.getBoundingClientRect()
            var tabs_top = document.getElementById('tabs_top_limit').getBoundingClientRect().top;
            var tabs_bot = document.getElementById('tabs_bot_limit').getBoundingClientRect().bottom;
            let height = screen.height - mesh_display_rect.top - (tabs_bot-tabs_top);
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
</script>

<div id='mesh_display' class='flex justify-center w-full'>
    <!-- Here goes the Three js display -->
</div>
<span id='tabs_top_limit'></span>
<Tabs style="underline">
    <TabItem open>
        <span slot="title">Position</span>
        <RangeInput property='pos' axis='x' interval={[-10, transformations.pos.x, 10]} step={0.1} on:change={handleTransformations} />
        <RangeInput property='pos' axis='y' interval={[-10, transformations.pos.y, 10]} step={0.1} on:change={handleTransformations} />
        <RangeInput property='pos' axis='z' interval={[-10, transformations.pos.z, 10]} step={0.1} on:change={handleTransformations} />
    </TabItem>
    <TabItem>
        <span slot="title">Rotation</span>
        <RangeInput property='rot' axis='x' interval={[-180, transformations.rot.x, 180]} step={0.1} on:change={handleTransformations} />
        <RangeInput property='rot' axis='y' interval={[-180, transformations.rot.y, 180]} step={0.1} on:change={handleTransformations} />
        <RangeInput property='rot' axis='z' interval={[-180, transformations.rot.z, 180]} step={0.1} on:change={handleTransformations} />
    </TabItem>
    <TabItem>
        <span slot="title">Scale</span>
        <RangeInput property='scale' axis='value' interval={[0, transformations.scale.value, 180]} step={0.1} on:change={handleTransformations} />
    </TabItem>
</Tabs>
<span id='tabs_bot_limit'></span>