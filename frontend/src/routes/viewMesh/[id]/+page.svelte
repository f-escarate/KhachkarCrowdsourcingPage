<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { init, animate, transform_stone } from '$lib/mesh_display';
    import RangeInput from '../../../components/RangeInput.svelte';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let transformations = {
        pos: {x: 0, y: 0, z: 0},
        rot: {x: 0, y: 0, z: 0},
        scale: {value: 0}
    }
    onMount(async () => {
        if(browser) {
            init(window.innerWidth/2, window.innerHeight, document.getElementById('mesh_display'), id);
            animate()
	    }
    });

    const handleTransformations = (e) => {
        const { property, axis, value } = e.detail;
        transformations[property][axis] = parseFloat(value);
        transform_stone(transformations);
    }
</script>

<h1 class='text-4xl font-bold'>Edit Khachkar</h1>
<div id='mesh_display' class='flex justify-center'>
    <!-- Here goes the Three js display -->
</div>
<div class='flex'>
    <div>
        <RangeInput label='Position' property='pos' axis='x' interval={[-10, 0, 10]} step={0.1} on:change={handleTransformations} />
        <RangeInput label='Position' property='pos' axis='y' interval={[-10, 0, 10]} step={0.1} on:change={handleTransformations} />
        <RangeInput label='Position' property='pos' axis='z' interval={[-10, 0, 10]} step={0.1} on:change={handleTransformations} />
    </div>
    <div>
        <RangeInput label='Rotation' property='rot' axis='x' interval={[-180, 0, 180]} step={0.1} on:change={handleTransformations} />
        <RangeInput label='Rotation' property='rot' axis='y' interval={[-180, 0, 180]} step={0.1} on:change={handleTransformations} />
        <RangeInput label='Rotation' property='rot' axis='z' interval={[-180, 0, 180]} step={0.1} on:change={handleTransformations} />
    </div>
    <RangeInput label='Scale' property='scale' axis='value' interval={[0, 0, 180]} step={0.1} on:change={handleTransformations} />
</div>