<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增商品</el-button>
        <el-select v-model="course" placeholder="请选择" clearable>
          <el-option
            v-for="item in courseList"
            :key="item.id"
            :label="`【${item.id}】- ${item.title} (${item.type})`"
            :value="item.id">
            <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
          </el-option>
        </el-select>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="resetFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.results.filter(
          (data) =>
            !search || data.title.toLowerCase().includes(search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
      <el-table-column label="商品ID" width="80">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>
      <el-table-column label="课程ID">
        <template slot-scope="scope">{{ scope.row.course }}</template>
      </el-table-column>
      <el-table-column label="商品类型">
        <template slot-scope="scope">{{ scope.row.type_description }}</template>
      </el-table-column>
      <el-table-column label="商品原价">
        <template slot-scope="scope">{{ scope.row.original_price }}</template>
      </el-table-column>
      <el-table-column label="商品售价">
        <template slot-scope="scope">{{ scope.row.price }}</template>
      </el-table-column>
      <el-table-column label="商品状态">
        <template slot-scope="scope">{{ scope.row.status_description }}</template>
      </el-table-column>
      <el-table-column label="商品描述">
        <template slot-scope="scope">{{ scope.row.description }}</template>
      </el-table-column>
      <el-table-column label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间">
        <template slot-scope="scope">
          <span>{{ scope.row.update_time }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="mini"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="mini"
            icon="el-icon-delete"
            :disabled="!checkPermission(['position_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-show="tableDataList.count>0"
      :total="tableDataList.count"
      :page-size.sync="listQuery.page_size"
      :current-page.sync="listQuery.page"
      @current-change="getList"
    ></el-pagination>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑产品' : '新增商品'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
      <el-row>
        <el-col :span="12">
          <el-form-item label="课程" prop="course">
            <el-select v-model="tableData.course" placeholder="请选择" @change="changeGetSCList">
              <el-option
                v-for="item in courseList"
                :key="item.id"
                :label="`【${item.id}】- ${item.title} (${item.type})`"
                :value="item.id">
                <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="关联期课" prop="term_course">
            <el-select v-model="tableData.term_course" placeholder="请选择">
              <el-option
                v-for="item in courseScList"
                :key="item.id"
                :label="`【期课ID:${item.id}】- 第${item.term_number}期`"
                :value="item.id">
                <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
        <el-form-item label="商品标题" prop="term_number">
          <el-input v-model="tableData.name" placeholder="商品标题"/>
        </el-form-item>
        <el-form-item label="商品原价(元)" prop="original_price">
          <el-input v-model="tableData.original_price" placeholder="商品价格，支持小数点后两位"/>
        </el-form-item>
        <el-form-item label="商品售价(元)" prop="price">
          <el-input v-model="tableData.price" placeholder="商品价格，支持小数点后两位"/>
        </el-form-item>
        <el-form-item label="商品描述" prop="description">
          <el-input v-model="tableData.description" placeholder="描述"/>
        </el-form-item>
        <el-form-item label="商品类型" prop="type">
          <el-select
            v-model="tableData.type"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品状态" prop="type">
          <el-select
            v-model="tableData.status"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getCourseList,
} from "@/api/course";
import {
  getProductById,
  getProductList,
  createProduct,
  updateProduct,
  deleteProduct
} from "@/api/product";
import { getScCourseList } from "@/api/sc_course";
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";

const defaultM = {};
export default {
  data() {
    return {
      tableData: {
        id: "",
        question_type: "",
        question_text: "",
        options: "",
        survey: "",
        create_time: "",
        update_time: "",
        term_course:''
      },
      search: "",
      tableDataList: {},
      courseScList:[],
      statusOptions: {},
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      courseList: [],
      course: null,
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'product',
        service: 'type'
      }
    };
  },
  computed: {},
  created() {
    this.getProductTypeList();
    this.getProductStatusList();
    this.getCourseList().then(() => {
      this.getList();
    });

  },
  methods: {
    checkPermission,
    getProductTypeList() {
      let query = {module: this.enumConfigQuery.module, service: 'type'};
      getEnumConfigList(query).then((response) => {
        this.typeOptions = response.data.results;
      })
    },
    changeGetSCList(){
      this.tableData.term_course = '';
      this.getScList();
    },
    getScList(){
        getScCourseList({course:this.tableData.course}).then((response) => {
          this.courseScList = response.data.results;
        });
    },
    getProductStatusList() {
      let query = {module: this.enumConfigQuery.module, service: 'status'};
      getEnumConfigList(query).then((response) => {
        this.statusOptions = response.data.results;
      })
    },
    getCourseList() {
      return new Promise((resolve, reject) => {
        getCourseList({}).then((response) => {
          this.courseList = response.data.results;
          if (this.courseList && this.courseList.length > 0) {
            this.course = this.courseList[0].id;
          }
          resolve()
        })
      })
    },
    getList() {
      this.listLoading = true;
      this.listQuery.course = this.course;
      getProductList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
        this.tableData = Object.assign({}, defaultM);
        this.dialogType = "new";
        this.dialogVisible = true;
        this.tableData.survey = this.course;
        this.$nextTick(() => {
            this.$refs["Form"].clearValidate();
        });
    },
    handleEdit(scope) {
        this.tableData = Object.assign({}, scope.row); // copy obj
        this.getScList();
        this.dialogType = "edit";
        this.dialogVisible = true;
        this.$nextTick(() => {
            this.$refs["Form"].clearValidate();
        });
    },
    handleDelete(scope) {
        this.$confirm("确认删除?", "警告", {
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            type: "error",
        }).then(async () => {
            await deleteProduct(scope.row.id);
            this.getList();
            this.$message({
                type: "success",
                message: "成功删除!",
            });
        }).catch((err) => {
            console.error(err);
        });
    },
    goToQuestionsPage(scope) {
        this.$router.push({name: 'questions', params: scope});
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateProduct(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createProduct(this.tableData).then((res) => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "新增成功",
                type: "success",
              });
            });
          }
        } else {
          return false;
        }
      });
    },
  },
};
</script>
