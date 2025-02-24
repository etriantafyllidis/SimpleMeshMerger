# Simple Mesh Merger
A quick Python script that merges multiple .obj files into a single .obj while keeping each mesh as a separate sub-object (useful for Unity, Unreal, etc.).

**Usage:**
Place your .obj files in the obj_files_to_merge folder (this repo includes 5 sample files).
Run: python merge_obj.py obj_files_to_merge output.obj
obj_files_to_merge is the folder with your .obj files.
output.obj is the merged result (default: merged_output.obj if omitted).

**Notes:**
OBJ format does not store pivot or scaling data, so you may need to adjust pivot/scale in your target engine.
No FBX support. Improvements to follow.
