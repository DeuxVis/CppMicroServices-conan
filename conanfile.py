from conans import ConanFile, CMake
from conans.util.files import load
import os
import re
from itertools import chain


class CppMicroServicesConan(ConanFile):
    name = 'CppMicroServices'
    version = '3.3.0'
    license = "Apache License - Version 2.0"
    description = "An OSGi-like C++ dynamic module system and service registry http://cppmicroservices.org"
    settings = ['os', 'compiler', 'build_type', 'arch']
    generators = ['cmake']
    url = 'https://github.com/pollen-metrology/CppMicroServices-conan.git'
    options = {
        'US_ENABLE_THREADING_SUPPORT': ['ON', 'OFF'],    # Enable threading support.
        'US_BUILD_SHARED_LIBS': ['ON', 'OFF'],           # Build shared libraries.
        'US_BUILD_TESTING': ['ON', 'OFF'],               # Build tests.
        'US_BUILD_EXAMPLES': ['ON', 'OFF'],              # Build example projects.
        'US_BUILD_DOC_HTML': ['ON', 'OFF'],              # Build the html documentation, as seen on docs.cppmicroservices.org.
        'US_BUILD_DOC_MAN': ['ON', 'OFF'],               # Build the man pages.
    }
    default_options = ('US_ENABLE_THREADING_SUPPORT=OFF',
                       'US_BUILD_SHARED_LIBS=ON',
                       'US_BUILD_TESTING=OFF',
                       'US_BUILD_EXAMPLES=OFF',
                       'US_BUILD_DOC_HTML=OFF',
                       'US_BUILD_DOC_MAN=OFF')
    cppmicroservices_bundles = ['framework', 'httpservice', 'shellservice', 'webconsole']
    build_dir = 'build'
    linked_libraries_filename = 'cppmicroservices_linked_libraries.txt'

    def source(self):
        cppmicroservices_url = 'https://github.com/CppMicroServices/CppMicroServices.git'
        release_tag = 'v{version}'.format(version=self.version)
        self.run("git clone {url} --branch {tag} --depth 1".format(url=cppmicroservices_url, tag=release_tag))

    def build(self):
        if not os.path.isdir(self.name):
            self.source()

        print ('### Settings ###')
        for (setting, val) in self.settings.iteritems():
            print( "{s} = {v}".format( s=setting, v=val ))

        print ('### Options ###')
        for (option, val) in self.options.iteritems():
            print( "{o} = {v}".format( o=option, v=val ))

        cmake = CMake(self)

        option_defines = {}
        for (option, val) in self.options.iteritems():
            option_defines[option] = val
        option_defines ['CMAKE_BUILD_TYPE'] = self.settings.build_type
        print( "### CONFIGURING ###" )
        cmake.configure(source_folder=self.name, build_folder=self.build_dir, defs=option_defines)

        print( "### BUILDING ###" )
        cmake.build()

        print( "### INSTALLING ###" )
        cmake.install()

        linked_libraries_file_path = "{build_dir}/{filename}".format(build_dir=self.build_folder, filename=self.linked_libraries_filename)
        with open(linked_libraries_file_path, 'w') as linked_libraries_file:
            linked_libraries_file.write('\n'.join(self._get_linker_libraries()))
            linked_libraries_file.close()

        print( "### PATCHING ###" )
        bf = self.build_folder.replace("\\", "/")
        findstr = bf + "/" + self.name
        replstr = "${CONAN_%s_ROOT}" % self.name.upper()

        print( "### Looking in *.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith(".cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)

        print( "### Looking in *.cmake files to replace '" + bf + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith(".cmake"):
                    self._replace_in_file(os.path.join(root, f), bf, replstr)

        findstr = replstr + '/build'
        print( "### Looking in *.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith(".cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)
                    
        findstr = 'INTERFACE_INCLUDE_DIRECTORIES "'
        replstr = findstr + replstr + "/include/cppmicroservices3;"
        print( "### Looking in *Targets.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith("Targets.cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)
                    
        findstr = 'message(FATAL_ERROR "Some (but not all) targets'
        replstr = '#' + findstr
        print( "### Looking in *Targets.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith("Targets.cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)
                    
        findstr = 'add_library(CppMicroServices SHARED IMPORTED)'
        replstr = 'if(NOT TARGET CppMicroServices)\n' + findstr + '\nendif(NOT TARGET CppMicroServices)\n'
        print( "### Looking in *Targets.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith("Targets.cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)
                    
        findstr = 'add_library(usHttpService SHARED IMPORTED)'
        replstr = 'if(NOT TARGET usHttpService)\n' + findstr + '\nendif(NOT TARGET usHttpService)\n'
        print( "### Looking in *Targets.cmake files to replace '" + findstr + "' by '" + replstr + "'" )
        allwalk = chain(os.walk(self.build_folder), os.walk(self.package_folder))
        for root, _, files in allwalk:
            for f in files:
                if f.endswith("Targets.cmake"):
                    self._replace_in_file(os.path.join(root, f), findstr, replstr)

    def package(self):
        # Module headers
        for bundle in self.cppmicroservices_bundles:
            # we copy headers from the src path as well because some of the public headers need these to compile
            src_path = "{src_dir}/{bundle}/src".format(src_dir=self.name, bundle=bundle)

            include_path = "{bundle}/include".format(bundle=bundle)
            src_include_path = "{src_dir}/{path}".format(src_dir=self.name, path=include_path)
            build_include_path = "{build_dir}/{path}".format(build_dir=self.build_dir, path=include_path)

            self.copy('*.h', dst=include_path, src=src_path)
            self.copy('*.h', dst=include_path, src=src_include_path)
            self.copy('*.h', dst=include_path, src=build_include_path)
            self.copy('*.tpp', dst=include_path, src=src_path)
            self.copy('*.tpp', dst=include_path, src=src_include_path)
            self.copy('*.tpp', dst=include_path, src=build_include_path)

        # Third party headers
        self.copy('*.h', dst='third_party', src="{src_dir}/third_party".format(src_dir=self.name))
        self.copy('*.tpp', dst='third_party', src="{src_dir}/third_party".format(src_dir=self.name))

        # Generated global includes
        build_include_path = "{build_dir}/include".format(build_dir=self.build_dir)
        self.copy('*.h', dst='include', src=build_include_path)
        self.copy('*.tpp', dst='include', src=build_include_path)

        # Built artifacts
        build_lib_dir = "{build_dir}/lib".format(build_dir=self.build_dir)
        package_lib_dir = "lib/{type}".format(type=self.settings.build_type)
        self.copy('*.so*', dst=package_lib_dir, src=build_lib_dir)  # In unix systems, the version number is appended
        self.copy('*.a', dst=package_lib_dir, src=build_lib_dir)
        # msvc places '.lib' files under the build type (Debug/Release) subdirectory
        self.copy('*.lib', dst=package_lib_dir, src=build_lib_dir, keep_path=False)

        # usWebConsole is built in the bin/main directory, need to check why
        # In unix systems, the version number is appended to the shared library
        build_bin_dir = "{build_dir}/bin".format(build_dir=self.build_dir)
        if self.settings.os == "Windows":
            build_bin_dir = "{build_dir}/bin/{type}".format( build_dir=self.build_dir, type=self.settings.build_type )
        package_bin_dir = "bin/{type}".format(type=self.settings.build_type)
        self.copy('*.so*', dst=package_lib_dir, src=build_bin_dir)
        self.copy('*.dll', dst=package_bin_dir, src=build_bin_dir)
        
        # Executables
        self.copy('usResourceCompiler3*', dst=package_bin_dir, src=build_bin_dir)
        self.copy('usShell3*', dst=package_bin_dir, src=build_bin_dir)

        self.copy('GettingStarted*', dst=package_bin_dir, src=build_bin_dir)
        self.copy('usTutorialDriver*', dst=package_bin_dir, src=build_bin_dir)
        self.copy('usWebConsoleDriver*', dst=package_bin_dir, src=build_bin_dir)
        
        # CMake info
        self.copy('CppMicroServicesConfig.cmake', dst='.', src=self.build_dir)
        self.copy('CppMicroServicesConfigVersion.cmake', dst='.', src=self.build_dir)
        self.copy('CppMicroServicesTargets.cmake', dst='.', src=self.build_dir)
        self.copy('us*Config.cmake', dst='.', src=self.build_dir)
        self.copy('us*ConfigVersion.cmake', dst='.', src=self.build_dir)
        self.copy('us*Targets.cmake', dst='.', src=self.build_dir)

        # CMake functions
        # We need to copy '*' because there are also template code files in the cmake directory
        self.copy('*', dst='cmake', src="{src_dir}/cmake".format(src_dir=self.name))

        # Linked libraries file
        self.copy(self.linked_libraries_filename, dst='.', src=self.build_dir)

    def package_info(self):
        """ Maybe we shouldn't link to every bundle that is built, and just link to the CppMicroServices one """
        # linked_libraries_file_path = "%s/%s" % (self.cpp_info.rootpath, self.linked_libraries_filename)
        # with open(linked_libraries_file_path, 'r') as linked_libraries_file:
        #     # Warning: This reads the whole file into memory, but we expect it to be small
        #     self.cpp_info.libs = linked_libraries_file.read().split()
        self.cpp_info.libs = ['CppMicroServices']
        if self.settings.os == 'Linux':
            self.cpp_info.libs += ['dl']

        self.cpp_info.includedirs += ["{bundle}/include".format(bundle=bundle)
                                      for bundle in self.cppmicroservices_bundles]

        # The self.copy function used in package() recursively copies files under subdirectories, but includes the full
        # path. For header includes to work, either the subdirectory paths must not be included when copying, or we add
        # the subdirectories as directories on the compilation include paths
        #
        # Private headers under 'core/src/**' that were copied into 'core/include/**'
        # Improvement: recursively include any directories underneath {bundle}/include
        self.cpp_info.includedirs += ["core/include/{core_private}".format(core_private=sub_dir)
                                      for sub_dir in ['bundle', 'service', 'util']]

    def _get_linker_libraries(self):
        # Extract dependencies for the CppMicroServices library, to be appended to self.cpp_info.libs
        # See http://stackoverflow.com/a/31940106/1576773
        self.run("cmake --graphviz={build_dir}/cppmicroservices.dot {build_dir}".format(build_dir=self.build_dir), False)

        dependencies = []
        # Old non windows compatible method kept commented out for reference
        #dependencies = None
        try:
            fname = "{build_dir}/cppmicroservices.dot.{lib}".format(build_dir=self.build_dir, lib=self.name)
            fin = open( fname, 'r' )

            for line in fin:
                out = re.sub( r'.*label="(.*)"\s.*', r'\1', line )
                if out != line:
                    dependencies.append( out.rstrip() )
                    #print( "### Found dependency '" + out.rstrip() + "' in '" + fname + "'" )

            #output_deps = StringIO()
            #command = "sed -n 's/.*label=\"\\(.*\\)\"\\s.*/\\1/p' {build_dir}/cppmicroservices.dot.{lib}".format(build_dir=self.build_dir, lib=self.name)
            #self.run(command, output_deps)
            #dependencies = output_deps.getvalue().split()
        finally:
            fin.close()
            #output_deps.close()
            if self.settings.os == "Windows":
                self.run("del /F {build_dir}\\cppmicroservices.dot*".format(build_dir=self.build_dir))
            else:
                self.run("rm -f {build_dir}/cppmicroservices.dot*".format(build_dir=self.build_dir))

        return dependencies

    def _replace_in_file(self, file_path, search, replace):
        content = load(file_path)
        found = content.find(search)
        if -1 != found:
            message = "_replace_in_file() found pattern in '%s' file." % (file_path)
            print( ">>> " + message)

        content = content.replace(search, replace)
        content = content.encode("utf-8")
        with open(file_path, "wb") as handle:
            handle.write(content)
            handle.close
