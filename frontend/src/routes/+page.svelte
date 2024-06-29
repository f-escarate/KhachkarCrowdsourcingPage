<script>
    import { onMount } from 'svelte';
    import { Button } from 'flowbite-svelte';
    import json_data from '$lib/home.json';
    import { base } from "$app/paths";
    import { addAnimationStyles } from '$lib/utils';
    import Cookies from 'js-cookie';
    import RightArrowIcon from '../components/icons/RightArrowIcon.svelte';
    import UploadCloudIcon from '../components/icons/UploadCloudIcon.svelte';
    let data = json_data.not_logged;

    const text_style = (idx) => {
        let margins = ['md:mt-[-2%]', 'md:mb-[-2%]'];
        let md_style = `md:w-2/3 lg:w-[60%] xl:w-[52%] md:text-xl z-10 ${margins[idx%2]}`; 
        let sm_style = 'w-full'
        return `h-full p-5 text-xl border-4 border-amber-500 bg-amber-300 text-black whitespace-pre-line ${md_style} ${sm_style}`;
    }
    const div_style = (idx) => {
        let paddings = ['pb-[2%]', 'pt-[2%]'];
        let directions = ['flex-row', 'flex-row-reverse']
        return `animated-div opacity-0 flex w-full md:my-10 relative h-full ${paddings[idx%2]} ${directions[idx%2]}`;
    }
    const img_style = (idx) => {
        let positions = ['right-0', 'left-0'];
        return `max-w-[60%] lg:min-w-[52%] h-full bottom-0 object-cover absolute invisible md:visible ${positions[idx%2]}`
    }

    onMount(() => {
        if (Cookies.get('access_token') !== undefined) {
            data = json_data.logged;
        }
        const targets = document.querySelectorAll('.animated-div');
        const div_anim_styles = ['animate-fade-right', 'animate-duration-500', 'animate-ease-out']
        addAnimationStyles(targets, div_anim_styles);
    });
</script>

<div class='flex flex-col h-full relative md:mx-10'>
    {#each data as element, i}
        <div class={div_style(i)}>
            <div class={text_style(i)}>
                {#each element.text as text_segment, i}
                    <p class='inline'>{text_segment}</p>
                    {#if element.links && element.links[i]}
                        <a class='underline italic font-bold'
                            href={element.links[i].external? element.links[i].url : `${base}${element.links[i].url}`}
                            target={element.links[i].external? '_blank' : ''}
                            rel={element.links[i].external? 'noopener noreferer' : ''}
                            >{element.links[i].label}</a>
                    {/if}
                {/each}
            </div>
            <img
                class={img_style(i)}
                src={`${base}${element.photo}`}
                alt={`${base}${element.photo}`}
            />
        </div>
    {/each}
    <div class='flex flex-col gap-2 animated-div opacity-0'>
        <h1 class='font-bold text-3xl my-8'>How does the automatic 3D model generation work?</h1>
        <div class='my-2 flex w-full h-full justify-center overflow-x-auto'>
            <div class='flex flex-col justify-between'>
                <img 
                    src={`${base}/gifs/videoForMeshing.gif`}
                    alt='Video for meshing'
                    class='h-full object-cover rounded-lg'
                />
                <h2 class='font-semibold mb-2 text-center'>Record a video</h2>
            </div>
            <div class='min-h-max w-1/2'>
                <RightArrowIcon sx='w-full h-full text-gray-800' />
            </div>
            <div class='min-h-max min-w-[20%] max-w-[80%] flex flex-col'>
                <UploadCloudIcon sx='w-full h-full text-cyan-600' />
                <h2 class='font-semibold mb-2 text-center'>Upload it to the website</h2>
            </div>
            <div class='min-h-max w-1/2'>
                <RightArrowIcon sx='w-full h-full text-gray-800' />
            </div>
            <div class='flex flex-col justify-between'>
                <img
                    src={`${base}/gifs/3DModelGif.gif`}
                    alt='3D model generated'
                    class='h-full object-cover rounded-lg'
                />
                <h2 class='font-semibold mb-2 text-center'>A mesh is created from the video</h2>
            </div>
        </div>
        <Button href={`${base}/tutorial/`} class='absolute bottom-[-50px] left-0 bg-amber-500 w-full'>
            Go to the tutorial
        </Button>
    </div>
</div>