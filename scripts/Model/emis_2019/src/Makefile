SHELL = /bin/sh
FC = ifort
FFLAGS = -fixed -132 -O3 -qoverride-limits -fno-alias -mp1 -fp-model precise -i-static -qopenmp -g -check all -traceback
PROGRAM = CREATE_EMIS_LIU
LIBS = -L/WORK/grmc_yyhong_1/liuyming/polyu/ubda-part1/ozone_cb05/model/CMAQv5.1/lib/x86_64/intel/ioapi_3.1/Linux2_x86_64ifort  -lioapi \
       -L${NETCDF}/lib -lnetcdf -lnetcdff
INCLUDE = -I/WORK/grmc_yyhong_1/liuyming/polyu/ubda-part1/ozone_cb05/model/CMAQv5.1/lib/x86_64/intel/ioapi_3.1/ioapi/fixed_src \
          -I${NETCDF}/include 

RAW = create.o

.F.o:
	$(FC) $(FFLAGS) $(INCLUDE) -c -o $@ $<

$(PROGRAM):	$(RAW)
	$(FC) $(FFLAGS) $(INCLUDE) -o $(@) $(RAW) $(LIBS)

clean:
	rm -f $(PROGRAM)  *.o *.core
