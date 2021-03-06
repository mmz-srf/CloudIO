#!/usr/bin/python

import sys
import getopt
import Cloudio
import configparser
import collections
import traceback

def inventory():
   """entry point that converts the list of all VMS to an ansible inventory."""
   inventory = configparser.RawConfigParser(allow_no_value=True)
   client = Cloudio.Cloudio()
   projects = client.getProjectIds()
   for i in projects:
      client.setProjectID(i)
      domain = client.getDomain()
      vmlist = client.getVMListByHame()
      sorted_vmlist = collections.OrderedDict(sorted(vmlist.items()))
      inventory.add_section(i)
      for vmname, vmdata in sorted_vmlist.iteritems():
         inventory.set(i, "%s.%s" %(vmname, domain) )
   inventory.write(sys.stdout)

def startvm():
   client = Cloudio.Cloudio()
   client.enableHttpRequestLogging()
   fqdn = sys.argv[1].split('.', 1)
   client.setProjectID(fqdn[1])
   jobid = client.startVM(fqdn[0])
   client.obsessJob(jobid)

def stopvm():
   client = Cloudio.Cloudio()
   client.enableHttpRequestLogging()
   fqdn = sys.argv[1].split('.', 1)
   client.setProjectID(fqdn[1])
   jobid = client.stopVM(fqdn[0])
   client.obsessJob(jobid)

def main(argv = sys.argv[1:]):
   vmname = None
   project = None
   command = None
   obsess = False
   debug = False
   log_http_requests = False

   try:
      opts, args = getopt.getopt(argv,"hodp:c:v:",["project=","command=", "vm=", "help", "obsess", "debug", "log-http-requests"])
   except getopt.GetoptError:
      print sys.argv[0] + ' -p <project> -c <command>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         command = "help"
      elif opt in ("-p", "--project"):
         project = arg
      elif opt in ("-c", "--command"):
         command = arg
      elif opt in ("-v", "--vm"):
         parts = arg.split('.', 1)
         vmname = parts[0]
         if len(parts)>1: project = parts[1]
      elif opt in ("-o", "--obsess"):
         obsess = True
      elif opt in ("-d", "--debug"):
         debug = True
      elif opt in ("--log-http-requests"):
         log_http_requests = True
   try:
      execute(command, project, vmname, obsess, log_http_requests)
   except:
      print >> sys.stderr, "Failed to execute '%s' in project %s for virtual machine %s" % (command, project, vmname)
      if debug: print >> sys.stderr, traceback.format_exc()
      sys.exit(1)

   sys.exit(0)

def execute(command, project, vmname = None, obsess = True, log_http_requests = False):
   jobid = None
   client = Cloudio.Cloudio()
   if project:
      client.setProjectID(project)
   if log_http_requests:
      client.enableHttpRequestLogging()
   project_arr = client.getProjectIds()
   if command == 'help':
      client.printHelp()
   elif command == 'listisos':
      client.getIsos(project_arr[project])
   elif command == 'listvms':
      client.printVirtualMachines()
   elif command == 'stopvm':
      if isinstance(vmname, str) & isinstance(project, str):
         jobid = client.stopVM(vmname)
      else:
         print "Error: vmname and project must be provided"
   elif command == 'startvm':
      if isinstance(vmname, str) & isinstance(project, str):
         jobid = client.startVM(vmname)
      else:
         print "Error: vmname and project must be provided"
   elif command == 'createvm':
      if isinstance(vmname, str) & isinstance(project, str):
         jobid = client.createVM(vmname)
      else:
         print "Error: vmname and project must be provided"
   elif command == 'destroyvm':
      if isinstance(vmname, str) & isinstance(project, str):
         msg = "Expunge vm "+vmname+" ?"
         expunge = raw_input("%s (y/N) " % msg).lower() == 'y'
         expunge = str(expunge).lower()
         jobid = client.destroyVM(vmname, expunge)
      else:
         print "Error: vmname and project must be provided"
   elif command == 'listprojects':
      client.printProjects()
   elif command == 'listdiskofferings':
      client.printDiskOfferings()
   elif command == 'listvolumes':
      client.printVolumes()
   else:
      raise "Unknown command %s".format(command)

   if obsess and jobid is not None:
      print "Running: ",
      client.obsessJob(jobid)


if __name__ == "__main__":
   main()