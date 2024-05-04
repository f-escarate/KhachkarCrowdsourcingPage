<script>
    import { onMount } from 'svelte';
    import data from '$lib/home.json';
    import { base } from "$app/paths";

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
        const targets = document.querySelectorAll('.animated-div');
        const options = {
            root: null, // use the viewport as the root
            rootMargin: '0px',
            threshold: 0.5, // change this value as needed, 0.5 means when 50% of the element is visible
        };

        for (let i = 0; i < targets.length; i++){
            let target = targets[i];
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-right');
                        entry.target.classList.add('animate-duration-500');
                        entry.target.classList.add('animate-ease-out');
                        observer.unobserve(entry.target);
                    }
                });
            }, options);

            if (target) 
                observer.observe(target);
        }
    });
</script>

<div class='flex flex-col h-full relative md:mx-10'>
    {#each data as element, i}
        <div class={div_style(i)}>
            <div class={text_style(i)}>
                {element.text}
            </div>
            <img
                class={img_style(i)}
                src={`${base}${element.photo}`}
                alt={`${base}${element.photo}`}
            />
        </div>
    {/each}
</div>