.SUFFIXES:

hammer_repo=https://github.com/bsg-external/hammer.git
hammer_dir=$(CURDIR)/hammer
hammer_branch=uw-ee477

cadence_plugin_repo=https://github.com/bsg-external/hammer-cadence-plugins.git
cadence_plugin_dir=$(CURDIR)/hammer-cadence-plugins
cadence_plugin_branch=uw-ee477

#synopsys_plugin_repo=/home/projects/ee477.2023wtr/repos/hammer-synopsys-plugins.git
#synopsys_plugin_dir=$(CURDIR)/hammer-synopsys-plugins
#synopsys_plugin_branch=uw-ee477

bsg_plugin_repo=https://github.com/bsg-external/hammer-bsg-plugins.git
bsg_plugin_dir=$(CURDIR)/hammer-bsg-plugins
bsg_plugin_branch=uw-ee477

fakeram_repo=https://github.com/bespoke-silicon-group/bsg_fakeram.git
fakeram_dir=$(CURDIR)/bsg_fakeram
fakeram_branch=uw-ee477

basejump_stl_repo=https://github.com/bespoke-silicon-group/basejump_stl.git
basejump_stl_dir=$(CURDIR)/../basejump_stl
basejump_stl_branch=uw_ee477_wi23

#ALL_TOOLS := hammer cadence_plugin synopsys_plugin bsg_plugin fakeram basejump_stl
ALL_TOOLS := hammer cadence_plugin bsg_plugin fakeram basejump_stl

install-tools: $(addprefix install., $(ALL_TOOLS)) $(CURDIR)/.pyyaml_touch

install.%: update.%
	# nothing else to do!

install.fakeram: install.%: update.%
	cd $($*_dir) && make tools

update.%: clone.%
	@echo "Running target -> $@"
	$(eval cur_branch=$(shell cd $($*_dir) && git symbolic-ref --short HEAD))
	test "$(cur_branch)" = "$($*_branch)" || (cd $($*_dir) && git checkout $($*_branch) && git submodule update --init --recursive)
	cd $($*_dir) && git pull origin $($*_branch)

clone.%:
	@echo "Running target -> $@"
	test -d $($*_dir) || git clone $($*_repo) $($*_dir)


$(CURDIR)/.pyyaml_touch: 
	pip3 install --user pyyaml
	touch $@

clean-tools:
	rm -rfv $(foreach v,$(ALL_TOOLS), $($v_dir)) $(CURDIR)/.pyyaml_touch


