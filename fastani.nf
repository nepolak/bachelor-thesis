params.inputs_folder = "mags"
params.inputs_index = "winner_genomes.csv"

nextflow.preview.output = true


process fastani {
    conda 'bioconda::fastani==1.34'
    cpus 64
    memory 64.GB
    time 48.h

    input:
    tuple val(name), path(genomes)

    output:
    tuple val(name), path("${name}")


    script:
    """
    printf "%s\n" ${genomes} > genome_list.txt
    fastANI -t ${task.cpus} --ql genome_list.txt --rl genome_list.txt -o ${name} --matrix
    """
}


workflow {
    main:
    species_groups = channel.fromPath(params.inputs_index)
        | splitCsv(header: true)
        | map { stuff -> [stuff.classification.replace(" ", "_"), file(new File(params.inputs_folder, stuff.spire_id + ".fa").toString())] }
        | groupTuple

    results =  species_groups
        | fastani

    publish:
    fastani_results = results | ifEmpty(["none", ""])
    // print("local: ")
    // results.local.view()

    // clusters_global = cluster_data_global
    // clusters_local = cluster_data_local
}


output {
    fastani_results {
        path "fastani_results/."
        index {
            path "fastani_results.csv"
            // header true
        }
    }
}
