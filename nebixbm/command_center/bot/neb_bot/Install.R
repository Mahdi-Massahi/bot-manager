packs <- c("xts", "formattable",
           "rredis", "crayon")

message("Downloading required packages for R...")
install.packages(packs,
                 quiet = F,
                 # repos = "https://cloud.r-project.org/",
                 INSTALL_opts = '--no-lock')

rm(packs)

q(save = "no")