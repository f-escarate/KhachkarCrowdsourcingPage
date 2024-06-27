<script>
    import { browser } from '$app/environment'; 
    import { onMount } from 'svelte';
    import { Tabs, TabItem, Button, Spinner, Progressbar, Popover, Modal } from 'flowbite-svelte';
    import { init, animate, transform_stone, transform_bounding_box, clear_scene, load_mesh } from '$lib/mesh_display';
    import { base } from '$app/paths'
    import { HOST } from '$lib/constants';
    import Cookies from 'js-cookie';
    import { auth_post_request } from '$lib/utils';
    import RangeInput from '../../../components/RangeInput.svelte';
    import QuestionIcon from '../../../components/icons/QuestionIcon.svelte';
    /** @type {import('./$types').PageData} */
	export let data;
    let id = data.id
    let isLoading = false;
    let modalTransform = false;
    let modalBox = false;
    const progress_obj = {
        loaded: false,
        progress: 0
    };
    const set_progress = (p, b) => {
        progress_obj.progress = p;
        progress_obj.loaded = b;
    };
    let transformations = {};
    let bounding_box_scales = {};
    const reset_transformations= () => {
        transformations = {
            pos: {x: 0, y: 0, z: 0},
            rot: {x: 0, y: 0, z: 0},
        };
    }
    const reset_bounding_box= () => {
        bounding_box_scales = {
            current: {x: 0, y: 0, z: 0},
            max: {x: 0, y: 0, z: 0}
        };
    }
    reset_transformations();
    reset_bounding_box();
    const set_bounding_box_scales = (max_scales) => {
        bounding_box_scales.current = {...max_scales};
        bounding_box_scales.max = {...max_scales};
        transform_bounding_box(bounding_box_scales.current);
    };
    
    onMount(async () => {
        if (Cookies.get('access_token') === undefined) {
            window.location.href = `${base}/enter/login`;
        }
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
    const checkNoTransformations = (transforms_data) => {
        let pos_0 = transforms_data.pos.x == 0 && transforms_data.pos.y == 0 && transforms_data.pos.z == 0;
        let rot_0 = transforms_data.rot.x == 0 && transforms_data.rot.y == 0 && transforms_data.rot.z == 0;
        return pos_0 && rot_0;
    }
    const checkBoundingBoxChanged = (bounding_box_data) => {
        for (let key in bounding_box_data.current) {
            if (bounding_box_data.current[key] != bounding_box_data.max[key])
                return true;
        }
        return false;
    }
    const send_data = async (data, endpoint) => {
        isLoading = true;
        const response = await auth_post_request(`${HOST}/${endpoint}/${id}/`, data, 'POST', true);
        const res = await response.json();
        isLoading = false;
        if(res.status == 'success') {
            alert('Stone exported');
            progress_obj.loaded = false;
            clear_scene();
            load_mesh(id, set_progress, set_bounding_box_scales);
            return true;
        } else if (res.status == 'error') {
            alert('Error: ', res.msg);
        } else {
            alert('Unknown error');
        }
        return false;
    }
    const export_stone = async () => {
        let data = JSON.stringify({
            pos: Object.values(transformations.pos),
            rot: Object.values(transformations.rot)
        })
        let ok = await send_data(data, 'set_mesh_transformations');
        if (ok)
            reset_transformations();
    }
    const send_bounding_box = async () => {
        let data = JSON.stringify(Object.values(bounding_box_scales.current));
        let ok = await send_data(data, 'crop_mesh');
        if (ok)
            reset_bounding_box();
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
    <div class='flex items-center justify-end flex-col md:flex-row gap-1'>
        <h1 class='text-3xl font-bold text-left w-full'>Mesh editor</h1>
        <Button class='bg-amber-600 hover:bg-amber-500 ml-2 my-auto flex' on:click={e => modalTransform=true}>
            <QuestionIcon sx='h-full text-white'/>
            <p class='font-bold max-w-[250px]'>How set mesh transformations?</p>
        </Button>
        <Button class='bg-orange-600 hover:bg-orange-500 ml-2 my-auto flex' on:click={e => modalBox=true}>
            <QuestionIcon sx='h-full text-white'/>
            <p class='font-bold max-w-[250px]'>How edit mesh bounding box?</p>
        </Button>
    </div>
    <Modal bind:open={modalTransform} title='How to upload a mesh?' width='w-1/2' autoclose outsideclose>
        <p class='font-semibold'>You can change the mesh transformations by sliding the bars that correspond to each property (rotations and translations).</p>
        <p class='text-amber-600'>Example:</p>
        <video class='w-full' controls>
            <source src={`${base}/videos/videoMeshTransformations.mp4`} type="video/mp4">
            <track kind="captions">
            Your browser does not support the video tag.
        </video>
    </Modal>
    <Modal bind:open={modalBox} title='How to upload a mesh?' width='w-1/2' autoclose outsideclose>
        <p class='font-semibold'>You can change the size of the bounding box by sliding the bars that correspond to the size of each axis.</p>
        <p class='text-amber-500 font-bold'>Important: The mesh looks a little different after cropping, but it looks better in the museum.</p>
        <p class='text-amber-600'>Example:</p>
        <video class='w-full' controls>
            <source src={`${base}/videos/videoMeshBox.mp4`} type="video/mp4">
            <track kind="captions">
            Your browser does not support the video tag.
        </video>
    </Modal>
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
    <div id='mesh_display' class='m-1 flex justify-center w-full'>
        <!-- Here goes the Three js display -->
    </div>
    <span id='tabs_bot_limit'></span>
    <div class='m-2 flex flex-col md:flex-row gap-4 justify-center items-center'>
        {#if isLoading}
            <Button disabled>
                <Spinner class="mr-2" size="4"/>
                Loading...
            </Button>
            <Button disabled color="purple">
                <Spinner class="mr-2" size="4"/>
                Loading...
            </Button>
            <p class='font-bold text-amber-600'>That process could take a while...</p>
        {:else}
            {#if checkNoTransformations(transformations)}
                <Button id="noStoneTransformations" disabled >Save stone transformations</Button>
                <Popover class="w-64 text-sm font-light " title="No transformations to apply" triggeredBy="#noStoneTransformations">
                    You must apply some transformations to the stone before saving them (position or rotation).
                </Popover>
                {#if checkBoundingBoxChanged(bounding_box_scales)}
                    <Button color="purple" on:click={send_bounding_box}>Crop mesh and save bounding box</Button>
                {:else}
                    <Button id="noBoundingBoxChanges" disabled color="purple">Crop mesh and save bounding box</Button>
                    <Popover class="w-64 text-sm font-light " title="No changes in bounding box" triggeredBy="#noBoundingBoxChanges">
                        You must change the bounding box before cropping the mesh.
                    </Popover>
                {/if}
            {:else}
                <Button on:click={export_stone}>Save stone transformations</Button>
                <Button id="saveTransformationsBefore"disabled color="purple">Crop mesh and save bounding box</Button>
                <Popover class="w-64 text-sm font-light " title="You must save transformations before cropping" triggeredBy="#saveTransformationsBefore">
                    You must save your stones transformations before cropping the mesh.
                </Popover>
            {/if}
        {/if}
    </div>
</div>
