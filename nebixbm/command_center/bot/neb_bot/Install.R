packs <- c("xts", "formattable",
           "rredis", "crayon")

install.packages(packs, 
                 quiet = T,
                 repos = "https://cloud.r-project.org/")

if (interactive())
  message("Required packages are installed(?).")

rm(packs)

q(status = T, save = "no")